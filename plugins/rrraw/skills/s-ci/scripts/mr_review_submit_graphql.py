"""GraphQL documents for mr-review-submit."""

REVIEWERS_QUERY = """
query($fullPath: ID!, $iid: String!) {
  project(fullPath: $fullPath) {
    mergeRequest(iid: $iid) {
      author { username }
      reviewers {
        nodes {
          username
          mergeRequestInteraction { reviewState }
        }
      }
    }
  }
}"""

SET_REVIEWERS_MUTATION = """
mutation($projectPath: ID!, $iid: String!, $usernames: [String!]!) {
  mergeRequestSetReviewers(input: {
    projectPath: $projectPath
    iid: $iid
    operationMode: APPEND
    reviewerUsernames: $usernames
  }) {
    mergeRequest { id }
    errors
  }
}"""

REQUEST_CHANGES_MUTATION = """
mutation($projectPath: ID!, $iid: String!) {
  mergeRequestRequestChanges(input: {
    projectPath: $projectPath
    iid: $iid
  }) {
    mergeRequest { id }
    errors
  }
}"""
