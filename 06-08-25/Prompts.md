Prompt 1:
Explain how is the stock adjustment logic handled in WMS

Prompt 2:
Create a WMS enhancement to automatically correct negative stock entries by syncing with ERP once every 6 hours. It should work silently in the background and update the stock ledger with a reconciliation remark. This logic must not interfere with putaway or picking operations.

Prompt 3:
Add a validation to prevent stock adjustment outside warehouse working hours (6am to 6pm).


Prompt 4:
Change the flow to allow supervisor approval before stock gets adjusted.

Prompt 5:
Restrict all stock adjustments to only be allowed inside the QC zone. If an operator tries to perform an adjustment outside QC, it should throw a validation error with a message. Ensure this check is enforced on both RDT and HHT interfaces.
