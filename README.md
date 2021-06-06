# piranha-python
An implementation of Uber's Piranha: a tool to automatically detect and remove usages of a given feature flag
preserving the code's behavior.

## Installation
Available for installation (for now) from the [test Pypi's repo](https://test.pypi.org/project/piranha-python):
```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ piranha-python
```
**Please notice that this is still an extremely early and incomplete version!**

## Usage
Start by initializing libCST's codemod commands in the project into which you'd like
to run Piranha:
```
python3 -m libcst.tool initialize .
```

Then add `piranha` to the `modules` section inside the
generated `.libcst.codemod.yaml` file.
The `modules` section should look like this:
```
modules:
- 'libcst.codemod.commands'
- 'piranha'
```

Then, finally, run Piranha passing the name of the feature flag that must be removed
and directory where it should look for Python source files:
```
python3 -m libcst.tool codemod codemods.PiranhaCommand --flag-name <FEATURE_FLAG_NAME> <directory_path>
```

Use the following command to check further options available to use from libCST's codemod and additional
argument that can be passed to Piranha:
```
python3 -m libcst.tool codemod codemods.PiranhaCommand -h
```

## Some intended features for upcoming versions:
- [ ] Support removing feature flag references from test code;
- [ ] Customize whether a feature flag is used as treatment or control;
- [ ] Customize how the feature flag is resolved (i.e. Piranha's `receiverType` and `methodName` configs);
- [ ] Better integration with Django (maybe?);
- [ ] Better integration with Flask (maybe?);
