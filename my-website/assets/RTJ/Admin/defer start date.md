<%* 
// suggester
let choice = await tp.system.suggester(["1week", "2week","3week","1month"], ["1week", "2week","3week","1month"], true, "defer for how long?")
let date
// if statement
switch(choice) {
	case "1week":
		date = moment().add(1, 'w').format("YYYY-MM-DD") 
		break;
	case "2week":
		date = moment().add(2, 'w').format("YYYY-MM-DD") 
		break;
	case "3week":
		date = moment().add(3, 'w').format("YYYY-MM-DD") 
		break;
	case "1month":
		date = moment().add(1, 'M').format("YYYY-MM-DD") 
		break;
}
// changing the property in the note
const file = tp.file.find_tfile(tp.file.path(true));
await app.fileManager.processFrontMatter(file, (frontmatter) => {
  frontmatter["start"] = date;
});
_%>