For PDF files that need to be submitted to Instructlab:

- Split the PDF files into chunks and convert each section into Markdown (MD) format.
- Create a new GitHub repository or use an existing one to store these Markdown files.
- Push the Markdown files to the chosen GitHub repository.
- Note the commit hash ID of this push.
- In the Instructlab taxonomy repository, create or update qna.yaml file.
- In the qna.yaml file, add an entry that includes:
    - The GitHub repository URL where you pushed the Markdown files
    - The commit hash ID from a previous step
    - Any additional metadata required by Instructlab
- Commit and push the updated qna.yaml file to the Instructlab taxonomy repository.
