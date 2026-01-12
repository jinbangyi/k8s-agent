1. requirements: `requirement`
user->guidance-chat: help me create a guidance for AI to `requirement`: `chat1`
2. the AI will generate a draft guidance for the requirement: `draft guidance`
user->review-chat: `draft guidance`, help me review the latest result of task: `chat1`
3. the AI will give you a review include: `suggestions`, `score`(from 1 to 10)

loop below steps until the score is greater than 9.9
user->guidance-chat: `suggestions`, help me improve the guidance based on the latest review.
4. the AI will generate an improved guidance: `draft guidance v2`
user->review-chat: `draft guidance v2`, help me review the latest result of task: `chat1`
5. the AI will give you a review include: `suggestions`, `score`(from 1 to 10)
