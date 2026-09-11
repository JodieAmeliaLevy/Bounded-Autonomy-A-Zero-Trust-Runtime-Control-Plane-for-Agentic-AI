# Provider adapters

Add model-provider adapters here.

Design requirements:
- keep provider SDK details outside the core control plane;
- record model/version and harness settings for every evaluation run;
- never silently grant tools based on provider defaults;
- normalize provider-specific tool calls into `ActionRequest` before policy evaluation;
- store secrets only in environment variables.
