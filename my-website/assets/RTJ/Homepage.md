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
properties:
  formula.relative due:
    displayName: r.due
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
                - '!file.path.contains("Admin")'
                - status != "waiting"
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
            - start >= today()
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
    name: new initiatives
    filters:
      and:
        - type == "initiative"
        - status == "not designed"
        - '!file.path.contains("Admin")'

```


> [!info]- Performance
> ```dataviewjs
> // Gather initiatives and their linked processes
> const categoryData = {
>     badTraits: {
>         totalProcesses: 0,
>         workingProcesses: 0
>     },
>     goodTraits: {
>         totalProcesses: 0,
>         workingProcesses: 0
>     },
>     worshipActions: {
>         totalProcesses: 0,
>         workingProcesses: 0
>     }
> };
> 
> // Define level thresholds and character names for each category
> const levels = {
>     badTraits: [
>         { threshold: 0, name: "Novice Wanderer" },
>         { threshold: 20, name: "Humble Aspirant" },
>         { threshold: 40, name: "Seeking Awareness" },
>         { threshold: 60, name: "Resolute Striver" },
>         { threshold: 80, name: "Courageous Overcomer" },
>         { threshold: 90, name: "Master of Resilience" },
>         { threshold: 100, name: "Grandmaster of Transformation" }
>     ],
>     goodTraits: [
>         { threshold: 0, name: "Eager Novice" },
>         { threshold: 20, name: "Steadfast Guardian" },
>         { threshold: 40, name: "Virtuous Champion" },
>         { threshold: 60, name: "Guiding Light" },
>         { threshold: 80, name: "Noble Supporter" },
>         { threshold: 90, name: "Sage of Kindness" },
>         { threshold: 100, name: "Paragon of Goodness" }
>     ],
>     worshipActions: [
>         { threshold: 0, name: "Curious Seeker" },
>         { threshold: 20, name: "Devout Practitioner" },
>         { threshold: 40, name: "Faithful Observer" },
>         { threshold: 60, name: "Inspiring Believer" },
>         { threshold: 80, name: "Dedicated Devotee" },
>         { threshold: 90, name: "Beacon of Faith" },
>         { threshold: 100, name: "Avatar of Piety" }
>     ]
> };
> 
> // Use a Set to track unique processes for each category
> const seenFiles = {
>     badTraits: new Set(),
>     goodTraits: new Set(),
>     worshipActions: new Set()
> };
> 
> // Gather data for initiatives
> dv.pages()
>     .filter(t => t.type === "initiative" && t.status !== "waiting")
>     .forEach(initiative => {
>         // Get inlinked processes
>         const linkedFiles = initiative.file.inlinks;
>         const initiativeKR = initiative.KR;
> 
>         linkedFiles.forEach(link => {
>             const process = dv.page(link.path);
>             if (process && process.status !== undefined && process.status !== "waiting") {
>                 // Count total processes and working processes for each category
>                 if (initiativeKR === "bad traits" && !seenFiles.badTraits.has(link.path)) {
>                     seenFiles.badTraits.add(link.path);
>                     categoryData.badTraits.totalProcesses++;
>                     if (process.status === "working") {
>                         categoryData.badTraits.workingProcesses++;
>                     }
>                 } else if (initiativeKR === "good traits" && !seenFiles.goodTraits.has(link.path)) {
>                     seenFiles.goodTraits.add(link.path);
>                     categoryData.goodTraits.totalProcesses++;
>                     if (process.status === "working") {
>                         categoryData.goodTraits.workingProcesses++;
>                     }
>                 } else if (initiativeKR === "worship actions" && !seenFiles.worshipActions.has(link.path)) {
>                     seenFiles.worshipActions.add(link.path);
>                     categoryData.worshipActions.totalProcesses++;
>                     if (process.status === "working") {
>                         categoryData.worshipActions.workingProcesses++;
>                     }
>                 }
>             }
>         });
>     });
> 
> // Function to calculate average and level
> const calculateStats = (data, category) => {
>     const totalProcesses = data.totalProcesses; // Total processes
>     const workingProcesses = data.workingProcesses; // Total working processes
> 
>     // Calculate the percentage score
>     const avg = totalProcesses > 0 ? (workingProcesses / totalProcesses * 100).toFixed(2) : 0;
> 
>     // Determine current level
>     let currentLevel = levels[category].findIndex(level => avg < level.threshold);
>     if (avg == 100) {
>         currentLevel = levels[category].length; // Last level
>     } else if (currentLevel === -1) {
>         currentLevel = levels[category].length - 1;
>     }
>     currentLevel = currentLevel > 0 ? currentLevel - 1 : currentLevel;
> 
>     const isLastLevel = avg == 100;
>     const nextLevel = isLastLevel ? currentLevel : Math.min(currentLevel + 1, levels[category].length - 1);
> 
>     const processesNeeded = isLastLevel
>         ? 0
>         : Math.ceil((levels[category][nextLevel].threshold / 100 * totalProcesses) - workingProcesses);
> 
>     return {
>         avg,
>         currentLevel: currentLevel + 1,
>         totalLevels: levels[category].length,
>         currentLevelName: levels[category][currentLevel].name,
>         nextLevelName: isLastLevel ? "None" : levels[category][nextLevel].name,
>         processesNeeded: Math.max(0, processesNeeded)
>     };
> };
> 
> // Calculate stats for each category
> const badTraitsStats = calculateStats(categoryData.badTraits, 'badTraits');
> const goodTraitsStats = calculateStats(categoryData.goodTraits, 'goodTraits');
> const worshipActionsStats = calculateStats(categoryData.worshipActions, 'worshipActions');
> 
> // Display results
> dv.paragraph(`==Bad Traits Score:== ${badTraitsStats.avg}%, Level: ${badTraitsStats.currentLevel}/${badTraitsStats.totalLevels} **(${badTraitsStats.currentLevelName})**`);
> dv.paragraph(`Next Level: ${badTraitsStats.nextLevelName} (**${badTraitsStats.processesNeeded}** processes needed)`);
> dv.paragraph(`==Good Traits Score:== ${goodTraitsStats.avg}%, Level: ${goodTraitsStats.currentLevel}/${goodTraitsStats.totalLevels} **(${goodTraitsStats.currentLevelName})**`);
> dv.paragraph(`Next Level: ${goodTraitsStats.nextLevelName} (**${goodTraitsStats.processesNeeded}** processes needed)`);
> dv.paragraph(`==Worship Actions Score:== ${worshipActionsStats.avg}%, Level: ${worshipActionsStats.currentLevel}/${worshipActionsStats.totalLevels} **(${worshipActionsStats.currentLevelName})**`);
> dv.paragraph(`Next Level: ${worshipActionsStats.nextLevelName} (**${worshipActionsStats.processesNeeded}** processes needed)`);
> 
> ```
> 
> ---
> 
> ```dataviewjs
> // Collect initiatives and percentages based on "KR" property
> let badTraitsInitiatives = [];
> let goodTraitsInitiatives = [];
> let worshipActionsInitiatives = [];
> let badTraitsPercentages = [];
> let goodTraitsPercentages = [];
> let worshipActionsPercentages = [];
> 
> // Gather initiatives and percentages
> dv.pages()
>     .filter(t => t.type == "initiative" && t.status !== "waiting")
>     .forEach(initiative => {
>         // Get the inlinks for the initiative file
>         let linkedFiles = initiative.file.inlinks;
> 
>         // Filter only inlinked pages that have the 'working' property
>         let validProcesses = linkedFiles
>             .map(link => dv.page(link.path))
>             .filter(p => p && p.status !== undefined && p.status !== "waiting");  // Include all files with the 'working' property
> 
>         // Filter those that have working = true
>         let workingProcesses = validProcesses.filter(p => p.status === "working");
> 
>         // Calculate the percentage of working processes
>         let totalProcesses = validProcesses.length;
>         let percentage = totalProcesses > 0 ? (workingProcesses.length / totalProcesses) * 100 : 0;
> 
>         // Sort initiatives and percentages based on the "KR" property
>         if (initiative.KR === "bad traits") {
>             badTraitsInitiatives.push(initiative.file.name);
>             badTraitsPercentages.push(percentage.toFixed(2));
>         } else if (initiative.KR === "good traits") {
>             goodTraitsInitiatives.push(initiative.file.name);
>             goodTraitsPercentages.push(percentage.toFixed(2));
>         } else if (initiative.KR === "worship actions") {
>             worshipActionsInitiatives.push(initiative.file.name);
>             worshipActionsPercentages.push(percentage.toFixed(2));
>         }
>     });
> 
> // Combine all unique initiatives for labels
> let allInitiatives = [...new Set([...badTraitsInitiatives, ...goodTraitsInitiatives, ...worshipActionsInitiatives])];
> 
> // Helper function to get percentage or zero if initiative is not in the list
> const getPercentage = (initiative, list, percentages) => {
>     let index = list.indexOf(initiative);
>     return index !== -1 ? percentages[index] : 0;
> }
> 
> // Prepare the chart data
> const chartData = {
>     type: 'radar',
>     data: {
>         labels: allInitiatives,
>         datasets: [
>             {
>                 label: 'Bad Traits',
>                 data: allInitiatives.map(i => getPercentage(i, badTraitsInitiatives, badTraitsPercentages)),
>                 backgroundColor: 'rgba(255, 99, 132, 0.2)',
>                 borderColor: 'rgba(255, 99, 132, 1)',
>                 borderWidth: 1,
>             },
>             {
>                 label: 'Good Traits',
>                 data: allInitiatives.map(i => getPercentage(i, goodTraitsInitiatives, goodTraitsPercentages)),
>                 backgroundColor: 'rgba(54, 162, 235, 0.2)',
>                 borderColor: 'rgba(54, 162, 235, 1)',
>                 borderWidth: 1,
>             },
>             {
>                 label: 'Worship Actions',
>                 data: allInitiatives.map(i => getPercentage(i, worshipActionsInitiatives, worshipActionsPercentages)),
>                 backgroundColor: 'rgba(75, 192, 192, 0.2)',
>                 borderColor: 'rgba(75, 192, 192, 1)',
>                 borderWidth: 1,
>             }
>         ]
>     },
>     options: {
>         responsive: true,
>         plugins: {
>             legend: {
>                 display: true,
>                 position: 'top'
>             },
>             tooltip: {
>                 callbacks: {
>                     label: function(tooltipItem) {
>                         return `${tooltipItem.dataset.label}: ${tooltipItem.raw}%`;
>                     }
>                 }
>             }
>         },
>         scales: {
>             r: {
>                 angleLines: {
>                     display: true
>                 },
>                 suggestedMin: 0,
>                 suggestedMax: 100,
>                 ticks: {
>                     stepSize: 20
>                 }
>             }
>         }
>     }
> };
> 
> // Render the chart using Chart.js
> window.renderChart(chartData, this.container);
> 
> ```
> 