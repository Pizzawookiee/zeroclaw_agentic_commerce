Setting up merchant agents in Zeroclaw

Take the contents of this repo and paste them into your '.zeroclaw' folder.

Check that you have the following folders (free to create folders):

/shared/skills/ucp_merchant_skills
/agents/my_merchant_agent

Under 'agents/my_merchant_agent' you should see skills to populate. Right now those skills are 'search catalog' and 'retrieve_product_info'.

After populating these skills we need to update config.toml file which is under '.zeroclaw'.

We need to add the following keys (watch out for duplicate keys when manually editing config, or Zeroclaw will fail to parse the file):

[skill_bundles.ucp_merchant_skills]

[a2a.server]
enabled = true

[agents]

[agents.my_merchant_agent]
... whatever settings you like for your agent
skill_bundles = ['ucp_merchant_skills']

[agents.my_merchant_agent.a2a]
published = true
exposed_skills = ['search_catalog', 'retrieve_product_info']

Getting info from an agent:
First run 'zeroclaw gateway'.
Then, from your terminal you should be able to run:
curl http://localhost:42617/.well-known/agents-card.json
curl http://localhost:42617/a2a/my_merchant_agent/.well-known/agent-card.json


Running a skill from an agent:
I haven't figured this out yet but this is my in-progress Microsoft Powershell command
"""
function Get-ZeroClawA2AText($response) {
  $response.result.artifacts |
    ForEach-Object { $_.parts } |
    Where-Object { $_.kind -eq "text" } |
    Select-Object -First 1 -ExpandProperty text
}

$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "message/send"
  params = @{
    message = @{
      role = "user"
      messageId = "msg-search-catalog-001"
      parts = @(
        @{
          kind = "text"
          text = "Use the search_catalog skill. Query: headphones. Return only valid JSON."
        }
      )
    }
    configuration = @{
      blocking = $false
      acceptedOutputModes = @("text")
    }
  }
} | ConvertTo-Json -Depth 20

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:42617/a2a/my_merchant_agent" `
  -ContentType "application/json" `
  -Body $body `
  -TimeoutSec 30

$taskId = $response.result.id

do {
  Start-Sleep -Seconds 2

  $taskBody = @{
    jsonrpc = "2.0"
    id = 2
    method = "tasks/get"
    params = @{
      id = $taskId
    }
  } | ConvertTo-Json -Depth 20

  $taskResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:42617/a2a/my_merchant_agent" `
    -ContentType "application/json" `
    -Body $taskBody `
    -TimeoutSec 30

  $state = $taskResponse.result.status.state
  Write-Host "Task state: $state"
} while ($state -eq "working" -or $state -eq "submitted")

Get-ZeroClawA2AText $taskResponse
"""
