Contribution Guidelines
=======================
The Armada project maintainers would like to thank you for your interest in
contributing to Armada. This document outlines the processes and procedures
involved in contributing to Armada.

Code of Conduct
---------------
By contributing to Armada, you are agreeing to uphold the
`Contributor Covenant Code of Conduct <https://github.com/att-comdev/armada/
blob/master/CODE_OF_CONDUCT.rst>`_. Please familiarize yourself with it
before contributing.

Support
-------
Project maintainers regularly monitor the Armada GitHub
`issues <http://github.com/att-comdev/armada/issues>`_ page for design and
development related questions. Maintainers will try to answer questions located
there as quickly as possible.

Reporting an Issue
------------------
All bugs and features are tracked using the Armada GitHub
`issues <http://github.com/att-comdev/armada/issues>`_ page. Before submitting
an issue, please check the
`troubleshooting guide <http://armada-helm.readthedocs.io/en/latest/operations/
guide-troubleshooting.html>`_. If the issue still persists, please file an
official bug report on the `issues <http://github.com/att-comdev/armada/
issues>`_ page if one does not already exist. When filing an issue, please
follow the issue template and be as descriptive as possible.

After an issue is created, project maintainers will assign labels indicating
the issue type.

+-------------+---------------------------------------------------------------+
| Label       | Description                                                   |
+=============+===============================================================+
| bug         | Indicates a confirmed bug or other unexpected behavior        |
+-------------+---------------------------------------------------------------+
| enhancement | Feature request                                               |
+-------------+---------------------------------------------------------------+
| question    | Indicates a question                                          |
+-------------+---------------------------------------------------------------+
| docs        | Assigned to issues indicating missing or incomplete           |
|             | documentation                                                 |
+-------------+---------------------------------------------------------------+
| duplicate   | Assigned to issues that are duplicates of previously reported |
|             | issues                                                        |
+-------------+---------------------------------------------------------------+
| help-wanted | Project maintainers would like community help resolving the   |
|             | reported issue                                                |
+-------------+---------------------------------------------------------------+
| invalid     | Assigned to indicate an invalid issue type                    |
+-------------+---------------------------------------------------------------+

Additionally, issues can also be assigned a label indicating their size or
complexity.

+-------------+---------------------------------------------------------------+
| Label       | Description                                                   |
+=============+===============================================================+
| size/small  | Smaller than average change                                   |
+-------------+---------------------------------------------------------------+
| size/medium | Average change size requiring an average amount of testing    |
|             | and review                                                    |
+-------------+---------------------------------------------------------------+
| size/large  | Larger than average change requiring heavy testing and review |
+-------------+---------------------------------------------------------------+
| starter     | Issue is a good fit for a new contributor                     |
+-------------+---------------------------------------------------------------+

If the issue type is not clear or more information is needed, project
maintainers will reach out in the comment section to request additional
details.

Submitting a Patch
------------------
This section focuses on the workflow and lifecycle of Armada patches.
Development specific information can be found in the Armada
`developers' guide <http://armada-helm.readthedocs.io/en/latest/
readme.html#getting-started>`_

Armada accepts patches through GerritHub changes. Each commit pushed to
GerritHub is recognized as a "change" (the equivalent of a GitHub pull
request). When a change is pushed to GerritHub for review, it contains an
initial patch set that shows all of the revised changes. When a Gerrit change
is amended, a new patch set is created to show the differences from the
previous patch set.

The general workflow for submitting a change is:

  1. Select an issue - select an issue from the Armada GitHub
     `issues <http://github.com/att-comdev/armada/issues>`_ page by commenting
     on the issue itself.
  2. Submit a GerritHub change for review.
  3. Review - Project maintainers and contributors will review the change on
     GerritHub and may request that additional patch sets be submitted before
     the change can be merged.
  4. Merge or close - the change is either merged or closed by the project
     maintainers.

Using GerritHub
~~~~~~~~~~~~~~~
In order to use GerritHub, you must first authorize GerritHub to access your
GitHub profile and import SSH public keys by signing in at
`gerrithub.io <http://gerrithub.io>`_.

In order to submit a change using GerritHub, the
`git review <https://docs.openstack.org/infra/git-review/>`_ tool must be
installed. Git-review can be installed using Python
`pip <https://pypi.python.org/pypi/pip>`_ by executing:

.. code-block:: bash

    pip install git-review

Git-review can also be installed on Ubuntu by executing:

.. code-block:: bash

    apt-get install git-review

After installing git-review, clone the Armada repository from GerritHub

.. code-block:: bash

    git clone https://review.gerrithub.io/att-comdev/armada

Change to the repository root directory and configure git-review to use
GerritHub. This will verify that login is possible using your imported
`SSH public keys <https://help.github.com/articles/
connecting-to-github-with-ssh/>`_.

.. code-block:: bash

    cd armada
    git review -s

If you require authentication over HTTPS, you will need to generate an
`HTTPS password <https://review.gerrithub.io/#/settings/http-password>`_.
Once you have generated an HTTPS password, add the repository to your remote
repositories

.. code-block:: bash

    git remote add gerrit https://<username>@review.gerrithub.io/a/att-comdev/armada

Now that your local repository is configured, create a local branch for your
change using the format `<TYPE>/<SCOPE>/<DESC>`, where `TYPE` is the type
of change (i.e. feat, bug, docs), `SCOPE` is the Armada component where
the change will occur (i.e. api, cli, source), and `DESC` is a hyphenated
description of the change (i.e. new-endpoints).

An example branch name for a feature that adds more API endpoints might be
`feat/api/new-endpoints`.

.. code-block:: bash

    git checkout -b <BRANCH-NAME>

When you are ready to submit your local changes for review, commit your
changes:

.. code-block:: bash

    git commit

Armada uses Karma inspired `Semantic Commit Messages
<http://karma-runner.github.io/0.13/dev/git-commit-msg.html>`_ for all changes.

.. code-block:: bash

    <TYPE>(<SCOPE>): <TITLE>

    <DESCRIPTION>

    Closes <ISSUE-REFERENCE>

In the above template, `TYPE` refers to the type of change, `SCOPE` refers to
the area where the change occurs (i.e. api, cli, source), `TITLE` is the title
of the commit message, `DESCRIPTION` is a description of the change, and
`ISSUE-REFERENCE` is a link to the GitHub issue the change addresses.

Below is a list of possible types:

+----------+-------------------------------------------------------+
| Type     | Description                                           |
+==========+=======================================================+
| feat     | Adds a new feature                                    |
+----------+-------------------------------------------------------+
| fix      | Fixes a confirmed bug or other unexpected behavior    |
+----------+-------------------------------------------------------+
| docs     | Documentation update                                  |
+----------+-------------------------------------------------------+
| style    | Reformats existing code to conform to the style guide |
+----------+-------------------------------------------------------+
| refactor | Refactors existing code to improve readability        |
+----------+-------------------------------------------------------+
| test     | Adds additional tests                                 |
+----------+-------------------------------------------------------+

.. NOTE::

    The scope component of a commit message may be committed if the change
    covers more than a single component of Armada.

An commit message for a change that adds a new API endpoint might resemble the
following example:

.. code-block:: bash

    feat(api): add new API endpoint

    New api endpoint /foo/status returns the status of foo.

    Closes #999 https://github.com/att-comdev/armada/issues/999

.. NOTE::

    It is necessary to leave a blank line between the commit title and
    description in order for a change to appear properly on GerritHub.

Since each commit is represented as a "change" in GerritHub, multiple commits
should be squashed into one commit before pushing to GerritHub for review. To
squash redundant commits, execute:

.. code-block:: bash

    git rebase -i

Change "pick" to "squash" next to every commit except for the one containing
the commit message you wish to use for your Gerrit change.

To push your change for review, execute:

.. code-block:: bash

    git review

Your change will now be visible on GerritHub for review. In order to amend your
change after pushing it for review, you will need to create additional
patch sets.

In order to create an additional patch set, modify your existing commit and
push your new changes for review

.. code-block:: bash

    git commit --amend
    git review

An additional patch set will now appear on the original GerritHub change.

Work in Progress
~~~~~~~~~~~~~~~~
Uploading changes that are not yet complete is highly encouraged in order to
receive early feedback from project maintainers and other contributors. To
label your change as a work in progress, leave a code review of your own
patch set with a vote of -1 and a comment indicating that your patch set is a
work in progress.

Rebasing A Commit
~~~~~~~~~~~~~~~~~
If changes have occurred to the master branch since your local branch was last
updated, you will need to rebase your commit with the new changes.

Update master locally

.. code-block:: bash

    git checkout master
    git remote update

Return to your branch and rebase with master

.. code-block:: bash

    git checkout <BRANCH>
    git rebase origin/master

After resolving all merge conflicts, resume the rebase

.. code-block:: bash

    git rebase --continue

Code Review Workflow
~~~~~~~~~~~~~~~~~~~~
Once a change is submitted to GerritHub, project maintainers and other
contributors will review it and leave feedback. In order for a change to be
merged, a change must have at least two +2 votes from project maintainers, and
must pass all Jenkins continuous integration tests.

Continuous Integration Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All patch sets submitted to the Armada GerritHub undergo continuous integration
testing performed by Jenkins. If the Jenkins build is successful, Jenkins will
leave a code review with a vote of +1. If the Jenkins build fails, Jenkins will
leave a code review with a vote of -1.

In order to ensure that your patch set passes the continuous integration tests
and conforms to the PEP8 style guide, execute:

.. code-block:: bash

    tox -e pep8
    tox -e py35
    tox -e coverage
