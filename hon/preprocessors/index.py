import os.path
import re
from .preprocessor import Preprocessor


def is_readme(file_path):
    # check to see if the file_path name matches case-insensitie "readme"
    f = os.path.basename(file_path)
    filename, _ = os.path.splitext(f)
    if 'readme' == filename.lower():
        return True
    return False


# fn warn_readme_name_conflict<P: AsRef<Path>>(readme_path: P, index_path: P) {
#     let file_name = readme_path.as_ref().file_name().unwrap_or_default();
#     let parent_dir = index_path.as_ref().parent().unwrap_or(index_path.as_ref());
#     warn!(
#         "It seems that there are both {:?} and index.md under \"{}\".",
#         file_name,
#         parent_dir.display()
#     );
#     warn!(
#         "mdbook converts {:?} into index.html by default. It may cause",
#         file_name
#     );
#     warn!("unexpected behavior if putting both files under the same directory.");
#     warn!("To solve the warning, try to rearrange the book structure or disable");
#     warn!("\"index\" preprocessor to stop the conversion.");
# }


class IndexPreprocessor(Preprocessor):
    _name = 'index'

    def run(self, book):
        # get the source directory
        # iterate over each book "item"
        # if the book item is a chapter (? not sure about this)
        #   and the chapter's path is a readme [file]
        #     then add assign that chapter to the "index.md" file, implicitly.
        #     but warn if there is a naming conflict
        # (previous code returned the modified book, since we have access to
        #  the app, and by proxy the books, we could just "modify it in place")
        pass

        # fn run(&self, ctx: &PreprocessorContext, mut book: Book) -> Result<Book> {
        #     let source_dir = ctx.root.join(&ctx.config.book.src);
        #     book.for_each_mut(|section: &mut BookItem| {
        #         if let BookItem::Chapter(ref mut ch) = *section {
        #             if is_readme_file(&ch.path) {
        #                 let index_md = source_dir.join(ch.path.with_file_name("index.md"));
        #                 if index_md.exists() {
        #                     warn_readme_name_conflict(&ch.path, &index_md);
        #                 }

        #                 ch.path.set_file_name("index.md");
        #             }
        #         }
        #     });

        #     Ok(book)
        # }



