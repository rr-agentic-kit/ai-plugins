"""GraphQL documents for pending-reviews."""

from glab import GLAB_LIST_PAGE_SIZE

REVIEW_QUEUE_QUERY = f"""
query($after: String) {{
  currentUser {{
    reviewRequestedMergeRequests(
      state: opened
      reviewState: UNREVIEWED
      first: {GLAB_LIST_PAGE_SIZE}
      after: $after
    ) {{
      pageInfo {{ endCursor hasNextPage }}
      nodes {{
        webUrl
        resolvableDiscussionsCount
        resolvedDiscussionsCount
      }}
    }}
  }}
}}"""
