---
type: initiative
designed: false
dependency: ""
waiting: false
start: ""
---
# kpi

# process/kbi

```dataview
list rows.file.link
where type = "process" and contains(initiative,this.file.link)
group by working
```

# documentation

# projects

```dataview
list
where completed = false and type = "project" and contains(initiative,this.file.link)
sort recurrence desc
```
