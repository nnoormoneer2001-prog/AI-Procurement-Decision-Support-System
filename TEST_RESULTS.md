# Testing

The system was tested using normal, error, ambiguous, and boundary cases.

| Test Case                   | Expected Result                | Status   |
| --------------------------- | ------------------------------ | -------- |
| Normal request              | `send_for_review`              | ✅ Passed |
| Cost greater than budget    | `ask_for_info`                 | ✅ Passed |
| Missing reason              | `ask_for_info`                 | ✅ Passed |
| Cost = Budget               | `send_for_review`              | ✅ Passed |
| Valid CSV request (REQ-001) | Data found and valid           | ✅ Passed |
| Missing budget (REQ-003)    | Validation error detected      | ✅ Passed |
| Negative cost (REQ-007)     | Validation error detected      | ✅ Passed |
| Pending approval (REQ-008)  | Validation error detected      | ✅ Passed |
| Human Review                | Approve / Reject / Re-review   | ✅ Passed |
| Session State               | Data preserved between actions | ✅ Passed |

## Result

All planned test cases passed successfully.

The system does not automatically approve procurement requests. Final decisions remain under human review.
