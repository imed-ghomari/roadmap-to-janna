`BUTTON[note, project, process, initiative]`
```meta-bind-button
label: Process
icon: ""
hidden: true
class: ""
tooltip: ""
id: process
style: default
actions:
  - type: command
    command: quickadd:choice:7653fa42-3bad-4114-9b75-67a456aeeebb

```
```meta-bind-button
label: Project
icon: ""
hidden: true
class: ""
tooltip: ""
id: project
style: default
actions:
  - type: command
    command: quickadd:choice:140c3af8-c123-48b3-aef5-b00c3ea03911

```
```meta-bind-button
label: Note
icon: ""
hidden: true
class: ""
tooltip: ""
id: note
style: primary
actions:
  - type: command
    command: quickadd:choice:00ffe41c-adf3-4392-ae8f-4ac3c2dc4cf9

```
```meta-bind-button
label: Initiative
icon: ""
hidden: true
class: ""
tooltip: ""
id: initiative
style: default
actions:
  - type: command
    command: quickadd:choice:9fb140ea-8cd3-4f17-9b56-40037f0f902e

```

```base
formulas:
  relative due: if(due, if(due == today(),"today", if(due - today() > 0, (due - today()), "+ " + (due - today()))), "")
  status sorting: |
    if(status == "blocking", 1,
      if(status == "blocked", 1,
      if(status == "not working", 2,
      if(status == "not done", 2,
      if(status == "waiting", 3,
      if(status == "working", 4,
      if(status == "done", 4,
      if(status == "1", 5,
      if(status == "2", 6,
      if(status == "3", 7, 
      if(status == "4", 8, 
      if(status == "5", 9, 
      if(status == "6", 10,    
    99)))))))))))))aliases
  total_process_count: file.backlinks.filter(value.asFile().properties.type == "process" && value.asFile().properties.status != "waiting").length
  working_process_count: file.backlinks.filter(value.asFile().properties.type == "process" && value.asFile().properties.status == "working").length
  progress_fraction: if(formula.total_process_count > 0, formula.working_process_count / formula.total_process_count, 0)
  Progress: '"███████████████".slice(0, (formula.progress_fraction * 15).floor()) + "░░░░░░░░░░░░░░░".slice(0, 15 - (formula.progress_fraction * 15).floor())'
  initiative done: if(formula.total_process_count - formula.working_process_count == 0, true, formula.total_process_count - formula.working_process_count)
properties:
  formula.relative due:
    displayName: r.due
  formula.initiative done:
    displayName: left
views:
  - type: table
    name: open
    filters:
      or:
        - or:
            - file.name.contains("/")
            - file.name.contains(":")
            - file.name.contains("|")
            - file.name.contains("?")
            - file.name.contains("<")
            - file.name.contains(">")
            - file.name.contains("*")
            - file.name.contains("conflict")
            - file.path.contains("Initiatives/_inbox")
            - and:
                - "!recurrence.isEmpty()"
                - due.isEmpty()
                - status == "working"
        - and:
            - or:
                - and:
                    - type == "project"
                    - status != "done"
                - and:
                    - type == "process"
                    - due
                    - due <= today()
                    - status == "working"
                - and:
                    - type == "process"
                    - status != "working"
                - and:
                    - type == "initiative"
                    - status == "not designed"
            - and:
                - '!file.path.contains("Admin")'
                - status != "blocked"
                - or:
                    - start.isEmpty()
                    - start <= now()
    order:
      - type
      - status
      - context
      - file.name
      - formula.relative due
      - due
      - start
    sort:
      - property: formula.status sorting
        direction: ASC
      - property: due
        direction: DESC
      - property: type
        direction: DESC
      - property: context
        direction: ASC
    columnSize:
      note.type: 95
      note.status: 95
      note.context: 123
      file.name: 396
      formula.relative due: 84
      note.due: 116
      note.start: 195
  - type: table
    name: stuck
    filters:
      and:
        - '!file.path.contains("Admin")'
        - or:
            - status == "waiting"
            - status == "blocked"
            - start > today()
    order:
      - type
      - status
      - file.name
      - start
    sort:
      - property: status
        direction: ASC
      - property: type
        direction: DESC
    columnSize:
      note.type: 95
      note.status: 95
      file.name: 315
      note.start: 192
  - type: table
    name: calendar
    filters:
      and:
        - or:
            - and:
                - type == "process"
                - status == "working"
                - due <= today()
                - due
            - and:
                - type == "project"
                - status != "done"
                - due <= today() + '30d'
                - due
        - '!file.path.contains("Admin")'
    order:
      - due
      - formula.relative due
      - file.name
    sort:
      - property: due
        direction: DESC
    columnSize:
      note.due: 116
      formula.relative due: 87
      file.name: 446
  - type: table
    name: performance
    filters:
      and:
        - type == "initiative"
        - '!file.path.contains("Admin")'
    order:
      - formula.Progress
      - formula.initiative done
      - KR
      - file.name
    sort:
      - property: KR
        direction: ASC
      - property: formula.progress_fraction
        direction: ASC
      - property: formula.initiative done
        direction: ASC
    columnSize:
      formula.Progress: 200
      file.name: 299
      note.KR: 124

```
