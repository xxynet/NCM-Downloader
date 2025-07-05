---
name: Bug report
about: Create a report to help us improve
title: "[BUG] "
labels: ["bug"]
assignees: xxynet
---

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: textarea
    id: desc
    attributes:
      label: Describe the bug / 描述这个Bug
      description: A clear and concise description of what the bug is. / 清晰准确的描述这个bug
      placeholder: 
    validations:
      required: false
  - type: textarea
    id: reproduce
    attributes:
      label: To Reproduce / BUG复现
      description: Steps to reproduce the behavior: / 复现BUG的步骤
      placeholder: 1. Go to '...'\n2. Click on '....'\n3. Scroll down to '....'\n4. See error
      value: ""
    validations:
      required: true
  - type: input
      id: os
      attributes:
        label: OS
        description: Which OS are you on?
        placeholder: Windows 10
      validations:
        required: true
  - type: input
      id: version
      attributes:
        label: Version
        description: Which version are you on?
        placeholder: 
      validations:
        required: true
  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Please copy and paste any relevant log output. This will be automatically formatted into code, so no need for backticks.
      render: shell