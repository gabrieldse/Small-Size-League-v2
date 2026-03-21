# Day 4: Development Workflow

Today you will learn how to contribute to the project by creating branches and making commits according to our standards.

*(todo - add actual commands to follow along)*

## Contribution Workflow

1. **Create a branch**:
   When starting a new task, always create a new branch from `main`. Keep the name descriptive:
   ```sh
   git checkout -b feature/your-feature-name
   ```

2. **Make commits**:
   Write clear and descriptive commit messages for your changes, using the format described in [style](../../style/style.md):
   ```sh
   git add .
   git commit -m "add: new behavior for striker robot"
   ```

3. **Push and Pull Request**:
   Once you are done, push your branch and open a PR (Pull Request) on the repository:
   ```sh
   git push origin feature/your-feature-name
   ```

   A pull request should not modify too many files or add too many features at once. For this initial learning phase, your pull request should not exceed 300 lines of code.

You can now proceed to [Day 5](./day5.md).
