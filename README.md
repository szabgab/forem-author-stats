Experimental GitHub Action to collect statistics for an author of a Forem-based site


Let's assume your username on GitHub is USERNAME

Create a GitHub repository. The name does not matter. e.g. call it `my-dev-to-stats`.

Create the directory `.github/workflows` and put the following file in it: `collect.yml`

```
...
```

USERNAME.github.io





http://github.szabgab.com/szabgab-dev-to-stats/

https://dev.to/settings/extensions


Settings / Secrets / Actions
    New repository secret

    Name: FOREM_API_KEY
    Secret: ....

Settins / Pages
    Custom domain:    devto.szabgab.com
    Enforce HTTPS     checked

