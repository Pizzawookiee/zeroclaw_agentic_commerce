# **Setting Up Merchant Agents in ZeroClaw**

This guide explains how to set up a dummy UCP-style merchant agent in ZeroClaw, expose it through A2A, and test the agent card and skill execution from the terminal.

---

## **1. Copy the Repo Contents**

Take the contents of this repo and paste them into your `.zeroclaw` folder.

Check that you have the following folders. Create them if they do not already exist:

```text
/shared/skills/ucp_merchant_skills
/agents/my_merchant_agent
```

Under:

```text
/shared/skills/ucp_merchant_skills
```

you should see skills to populate.

Right now, those skills are:

```text
search_catalog
retrieve_product_info
```
You can also change the catalog by editing 'catalog.json' in the /agents/my_merchant_agent/workspace.

---

## **2. Update `config.toml`**

After populating the skills, update your `config.toml` file inside the `.zeroclaw` folder.

Add the following keys.

Be careful not to create duplicate keys when manually editing the config file, or ZeroClaw may fail to parse it.

```toml
[skill_bundles.ucp_merchant_skills]

[a2a.server]
enabled = true

[agents]

[agents.my_merchant_agent]
# Add whatever settings you like for your agent here.
skill_bundles = ["ucp_merchant_skills"]

[agents.my_merchant_agent.a2a]
published = true
exposed_skills = ["search_catalog", "retrieve_product_info"]
```

---

## **3. Getting Info From an Agent**

First, run the ZeroClaw gateway:

```powershell
zeroclaw gateway
```

Then, from your terminal, you should be able to run:

```powershell
curl http://localhost:42617/.well-known/agents-card.json
```

You can also fetch the A2A Agent Card for the merchant agent:

```powershell
curl http://localhost:42617/a2a/my_merchant_agent/.well-known/agent-card.json
```

---

## **4. Running a Skill From an Agent**

This is the current in-progress Microsoft PowerShell command for calling the `search_catalog` skill through A2A.

```powershell
$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "message/send"
  params = @{
    message = @{
      role = "user"
      parts = @(
        @{
          kind = "text"
          text = "Use the search_catalog skill. Query: headphones. Return only valid JSON in the UCP-shaped catalog search response format."
        }
      )
    }
  }
} | ConvertTo-Json -Depth 20

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:42617/a2a/my_merchant_agent" `
  -ContentType "application/json" `
  -Body $body

$response | ConvertTo-Json -Depth 50
```

---

## **5. Notes**

The merchant agent currently exposes two skills:

```text
search_catalog
retrieve_product_info
```

These skills are intended to return UCP-shaped catalog responses, but the agent is still exposed through A2A rather than through a full native UCP implementation.

For full UCP compliance, a separate UCP discovery/profile endpoint would likely still be needed.
