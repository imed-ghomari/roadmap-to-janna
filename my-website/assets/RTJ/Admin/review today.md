<%* 
const date = moment().add(1, 'M').format("YYYY-MM-DD")
const file = tp.file.find_tfile(tp.file.path(true));
await app.fileManager.processFrontMatter(file, (frontmatter) => {
  frontmatter["review"] = date;
});
_%>