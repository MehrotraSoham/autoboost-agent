from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from config.models import Post, FilterResult
from config.llm import get_llm

NEGATIVE_REACTION_THRESHOLD = 0.20
NEGATIVE_COMMENT_THRESHOLD = 0.30


class _SentimentOutput(BaseModel):
    negative_count: int
    total_count: int
    negative_ratio: float


async def run(post: Post) -> FilterResult:
    """
    Two-stage negativity gate. Returns FilterResult with passed=False
    and a suppressed_reason if either stage fails.

    Stage 1: reaction ratio — (angry + sad) / total_reactions > 20%
    Stage 2: comment sentiment via Claude — negative comments > 30%
    """
    # Stage 1 — reaction ratio
    negative_reaction_ratio = 0.0
    if post.total_reactions > 0:
        negative_reaction_ratio = (
            post.angry_reactions + post.sad_reactions
        ) / post.total_reactions

        if negative_reaction_ratio > NEGATIVE_REACTION_THRESHOLD:
            return FilterResult(
                post_id=post.post_id,
                passed=False,
                suppressed_reason=(
                    f"Stage 1 failed: {negative_reaction_ratio:.1%} negative reactions "
                    f"(threshold: {NEGATIVE_REACTION_THRESHOLD:.0%})"
                ),
                negative_reaction_ratio=round(negative_reaction_ratio, 3),
            )

    # Stage 2 — comment sentiment
    negative_comment_ratio = 0.0
    if post.recent_comments:
        negative_comment_ratio = await _analyze_sentiment(post.recent_comments)

        if negative_comment_ratio > NEGATIVE_COMMENT_THRESHOLD:
            return FilterResult(
                post_id=post.post_id,
                passed=False,
                suppressed_reason=(
                    f"Stage 2 failed: {negative_comment_ratio:.1%} negative comments "
                    f"(threshold: {NEGATIVE_COMMENT_THRESHOLD:.0%})"
                ),
                negative_reaction_ratio=round(negative_reaction_ratio, 3),
                negative_comment_ratio=round(negative_comment_ratio, 3),
            )

    return FilterResult(
        post_id=post.post_id,
        passed=True,
        negative_reaction_ratio=round(negative_reaction_ratio, 3),
        negative_comment_ratio=round(negative_comment_ratio, 3),
    )


async def _analyze_sentiment(comments: list[str]) -> float:
    """Use the configured LLM to classify comments and return the negative ratio."""
    llm = get_llm(max_tokens=256)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a social media sentiment classifier. "
            "Given a list of comments, count how many are NEGATIVE (complaints, anger, disappointment). "
            "Return a JSON object with: negative_count (int), total_count (int), negative_ratio (float 0-1).",
        ),
        ("human", "Classify these comments:\n{comments}"),
    ])

    chain = prompt | llm.with_structured_output(_SentimentOutput)
    result: _SentimentOutput = await chain.ainvoke(
        {"comments": "\n".join(f"- {c}" for c in comments)}
    )
    return result.negative_ratio
