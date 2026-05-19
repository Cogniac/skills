# Integration App RBAC

****Feature Restriction: Integration App Code Access by Role****

## ****Overview****

To improve security and enforce role-based access control (RBAC), a new feature has been implemented that restricts access to the ****Code**** section of integration applications. Only users with the role of `tenant_user` ****or above**** can view or edit the code. Users with `tenant_viewer` ****or below**** will not see the code section and will receive a message about insufficient permissions (pending frontend message implementation).

---

## ****Authorized Roles****

The following roles are ****allowed**** to view/edit code in integration apps:

- `tenant_admin`
- `tenant_user`
- `meraki_admin`

The following roles are ****not allowed**** to view/edit code in integration apps:

- `tenant_billing`
- `tenant_viewer`
- `tenant_ops`
- `annotator`
- `expert_annotator`
