# AI Usage Report — AI-Assisted Box Selection System

## AI Tools Used

During the development of this project, I used AI as a development assistant rather than an autonomous code generator. All AI-generated suggestions were reviewed, tested, and modified where necessary before being committed.

### Tools Used

* **ChatGPT (OpenAI)**

  * Discussing the overall Django project architecture.
  * Reviewing the project structure.
  * Improving the README and documentation.
  * Brainstorming edge cases for the recommendation engine.
  * Discussing testing strategy and project organization.

* **Claude (via Opencode CLI)**

  * Drafting boilerplate code.
  * Generating and refactoring unit tests.
  * Assisting with API integration changes.
  * Suggesting code cleanup and refactoring.
  * Helping debug implementation issues.

---

# Representative Prompts Used

The following are representative examples of the prompts I used throughout development.

## ChatGPT

* Suggest a clean Django project architecture for a box recommendation system.
* Should the packing engine be separated into a service layer?
* Review my README and suggest improvements.
* Suggest additional edge cases for testing the recommendation engine.
* Review my project structure and identify possible improvements.
* Help document the API and testing process.
* Review documentation before submission.

## Claude (Opencode CLI)

* Add missing tests for the packing engine.
* Remove unused imports and clean up the test suite.
* Replace the existing AI integration with Google Gemini.
* Generate an AI recommendation explainer class.
* Create unit tests for the AI explainer.
* Help debug API integration issues.
* Suggest refactoring for cleaner code.

---

# AI Usage Log

I treated AI as a pair programmer. It helped generate initial implementations and suggestions, but I reviewed every change before accepting it. Several AI suggestions required corrections before they were suitable for the project.

---

## 1. Test Cleanup and Additional Test Cases

### What I asked

* Add missing tests for the packing engine.
* Add tests for sorting, placement coordinates, orientations, and empty input.
* Rename a confusing test.
* Remove unused imports.

### Output Accepted

* Generated additional unit tests.
* Improved overall test coverage.
* Removed unused imports.
* Suggested better organization of the test suite.

### Output Rejected or Modified

* The generated `test_large_product_and_small_product` used a small product of `2×2×2`. Since the remaining space in the box was still very large, the sorting heuristic was not actually being exercised. I changed the smaller product to `2×10×10` so the packing order meaningfully affected the result.
* The placement of the `Http404` import needed additional correction before it was properly organized.
* One recommendation test duplicated the behavior of an existing test. I replaced it with:

  * `test_quantity_affects_box_selection`
  * `test_skips_box_with_insufficient_weight_capacity`

### Mistakes Identified

* Weak test case that did not validate the intended behavior.
* Import cleanup was incomplete.
* Redundant recommendation test.

### Status

Accepted after manual review and correction.

---

## 2. AI Integration (Google Gemini)

### What I asked

Replace the existing AI integration with Google's Gemini API to generate natural-language explanations for box recommendations.

### Output Accepted

* Integrated the Google Gemini API.
* Added support for `GEMINI_API_KEY`.
* Generated structured explanations for recommended boxes.
* Connected the AI explanation layer with the recommendation service.

### Output Rejected or Modified

* Updated the generated implementation to match my project structure.
* Adjusted the prompt to produce more concise recommendation explanations.
* Added exception handling so recommendations still work when Gemini is unavailable.

### Mistakes Identified

* The generated request format required adjustments to match the Gemini API.
* Additional exception handling was needed for API failures.
* The prompt wording was refined to produce clearer recommendation explanations.

### Status

Accepted after manual verification and correction.

---

## 3. AI Recommendation Explainer

### What I asked

Create an `AIRecommendationExplainer` class that generates a natural-language explanation for the selected shipping box.

### Output Accepted

* Initial class implementation.
* Prompt generation logic.
* API integration.
* Mocked unit tests.

### Output Rejected or Modified

* Updated environment variable references to `GEMINI_API_KEY`.
* Improved generated docstrings.
* Updated the unit tests to match the final implementation.

### Mistakes Identified

* The initial implementation required updates to use the final `GEMINI_API_KEY` configuration.
* Minor documentation improvements were required.

### Status

Accepted after review.

---

## 4. ChatGPT Discussions

ChatGPT was primarily used for design discussions rather than direct code generation.

### Topics Discussed

* Django application structure.
* Separation of business logic from views.
* Recommendation service architecture.
* README improvements.
* Project documentation.
* Edge cases for the recommendation algorithm.
* Test planning.
* Submission checklist.

### Output Accepted

* Cleaner project organization.
* Better documentation structure.
* Additional testing ideas.
* Suggestions for improving repository presentation.

### Output Modified

* Folder organization was adjusted to match my implementation.
* Documentation was edited to accurately reflect the final project.

### Mistakes Identified

No implementation bugs were introduced because these discussions were primarily architectural and documentation-focused.

---

## Code Review Process

AI-generated suggestions were never committed directly.

For every accepted suggestion, I:

- Reviewed the generated code against the project requirements.
- Modified the implementation where necessary.
- Tested the changes locally.
- Verified functionality through unit tests and API testing.
- Committed the code only after it behaved as expected.

---

# Verification Steps

No AI-generated code was committed without verification.

Every accepted suggestion was manually reviewed and validated using one or more of the following:

* Running the Django test suite.
* Manual API testing using Postman.
* Reviewing generated code before committing.
* Verifying recommendation results for correctness.
* Testing edge cases such as:

  * exact box fit
  * insufficient weight capacity
  * multiple product quantities
  * unavailable boxes
  * empty orders

---

# Test Verification

The project was tested after every major change.

```bash
python manage.py test
```

All tests passed successfully after the final implementation.

---

# My Contribution

AI was used to accelerate development, but I remained responsible for the implementation and final decisions throughout the project.

My responsibilities included:

* Designing the overall project structure.
* Implementing and integrating the recommendation workflow.
* Reviewing every AI-generated suggestion before accepting it.
* Identifying incorrect AI-generated outputs.
* Configuring and integrating the Google Gemini API into the recommendation workflow.
* Adding robust API error handling.
* Replacing weak or redundant tests with more meaningful coverage.
* Running and verifying the complete test suite.
* Reviewing and improving project documentation before submission.

---

# Summary

| Requirement                          | Details                                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------------------- |
| AI tools used                        | ChatGPT, Claude (Opencode CLI)                                                            |
| Representative prompts included      | Yes                                                                                       |
| Accepted outputs documented          | Yes                                                                                       |
| Rejected/modified outputs documented | Yes                                                                                       |
| AI mistakes identified               | Gemini request formatting adjustments, additional error handling, weak test case, import cleanup issue    |
| Verification steps                   | Manual review, Django tests, Postman testing, functional verification                     |
| Final responsibility                 | All accepted code was reviewed, integrated, tested, and verified by me before submission. |

