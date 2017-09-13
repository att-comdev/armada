Contribution Guidelines
=========================
The Armada project maintainers would like to thank you for your interest in contributing to Armada. This document outlines the processes and procedures involved in contributing to Armada.

Code of Conduct
---------------
By contributing to Armada, you are agreeing to uphold the `Contributor Convenant Code of Conduct <CODE_OF_CONDUCT.rst>`_. Please familiarize yourself with it before contributing.

Support
-------
Project maintainers regularly monitor the Armada GitHub `issues <github.com/att-comdev/armada/issues>`_ page for design and development related questions. Maintainers will try to answer questions located there as quickly as possible.

Reporting an Issue
------------------
All bugs and features are tracked using the Armada GitHub `issues <github.com/att-comdev/armada/issues>`_ page. Before submitting an issue, please check the `troubleshooting guide <docs/source/operations/guide-troubleshooting.rst>`_. If the issue still persists, please file an official bug report on the `issues <github.com/att-comdev/armada/issues>`_ page if one does not already exist. When filing an issue, please follow the issue template and be as descriptive as possible.

After an issue is created, project maintainers will assign labels indicating the issue type. 

+-------------+------------------------------------------------------------------------------+
| Label       | Description                                                                  |
+=============+==============================================================================+
| bug         | Indicates a confirmed bug or other unexpected behavior                       |
+-------------+------------------------------------------------------------------------------+
| ehancement  | Feature request                                                              |
+-------------+------------------------------------------------------------------------------+
| question    | Indicates a question                                                         |
+-------------+------------------------------------------------------------------------------+
| docs        | Assigned to issues indicating missing or incomplete documenation             |
+-------------+------------------------------------------------------------------------------+
| duplicate   | Assigned to issues that are duplicates of previously reported issues         |
+-------------+------------------------------------------------------------------------------+
| help-wanted | Project maintainers would like community help resolving the reported issue   |
+-------------+------------------------------------------------------------------------------+
| invalid     | Assigned to indicate an invalid issue type                                   |
+-------------+------------------------------------------------------------------------------+

Additionally, issues can also be assigned a label indicating their size or complexity:

+-------------+------------------------------------------------------------------------------+
| Label       | Description                                                                  |
+=============+==============================================================================+
| size/small  | Smaller than average change                                                  | 
+-------------+------------------------------------------------------------------------------+
| size/medium | Average change size requiring an average amount of testing and review        |
+-------------+------------------------------------------------------------------------------+
| size/large  | Larger than average change requiring heavy testing and review                |
+-------------+------------------------------------------------------------------------------+
| starter     | Issue is a good fit for a new contributor                                    |
+-------------+------------------------------------------------------------------------------+

If the issue type is not clear or more information is needed, project maintainers will reach out in the comment section to request additional details.

Submitting a Patch
------------------
This section focuses on the workflow and lifecycle of Armada patches. Development specific information can be found in the Armada `developers' guide <docs/source/development/getting-started.rst>`_. 

Armada accepts patches through GerritHub changes. Each commit pushed to GerritHub is recognized as a "change" (the equivalent of a GitHub pull request). When a change is pushed to GerritHub for review, it contains an intial patchset that shows all of the revised changes. When a Gerrit change is amended, a new patchset is created to show the differences from the previous patchset. 

The general workflow for submitting a change is:

1. Select an issue - select an issue from the Armada GitHub `issues <github.com/att-comdev/armada/issues>`_ page by commenting on the issue itself.
2. Submit a GerritHub change for review.
3. Review - Project maintainers and contributors will review the change on GerritHub and may request that additional patchsets be submitted before the change can be merged.
4. Merge or close - the change is either merged or closed by the project maintainers.

Using GerritHub
~~~~~~~~~~~~~~~
In order to use GerritHub, you must first authorize GerritHub to access your GitHub profile and import SSH public keys by signing in at `gerrithub.io <gerrithub.io>`_.

In order to submit a change using GerritHub, git-review must be installed. To install git-review on Ubuntu execute:

.. code-block:: bash

    apt-get install git-review

Clone the Armada repository from GerritHub

.. code-block:: bash

    git clone https://review.gerrithub.io/att-comdev/armada

Change to the repository root directory and configure git-review to use GerritHub. This will verify that login is possible using your imported `SSH public keys <https://help.github.com/articles/connecting-to-github-with-ssh/>`_.

.. code-block:: bash

    cd armada
    git review -s

If you require authentication over HTTPS, you will need to generate an `HTTPS password <https://review.gerrithub.io/#/settings/http-password>`_. Once you have generated an HTTPS passowrd, add the repository to your remote repositories

.. code-block:: bash

    git remote add gerrit https://<username>@review.gerrithub.io/a/att-comdev/armada
                   
Now that your local repository is configured, create a local branch for your change using the format `<TYPE>/<COMPONENT>/<DESC>`, where `TYPE` is the type of change (i.e. feat, bug, docs), `COMPONENT` is the Armada component where the change will occur (i.e. api, cli, source), and `DESC` is a hyphenated description of the change (i.e. new-endpoints). 

An example branch name for a feature that adds more API endpoints might be `feat/api/new-endpoints`. 

.. code-block:: bash

    git checkout -b <BRANCH-NAME>

When you are ready to submit your local changes for review, commit your changes:

.. code-block:: bash

    git commit

When creating a commit, prefix the title with the type of commit and use a bullet-point description to explain the change. An example of a feature commit message:

.. code-block:: bash

    [feat] Commit Title

    - Detailed bullet-point description of change

.. NOTE::

    It is necessary to leave a blank line between the commit title and desciption in order for a change to appear properly on GerritHub.

Since each commit is represented as a "change" in GerritHub, multiple commits should be squashed into one commit before pushing to GerritHub for review. To squash redundant commits, execute:

.. code-block:: bash

    git rebase -i

Change "pick" to "squash" next to every commit except for the one containing the commit message you wish to use for your Gerrit change.

To push your change for review, execute:

.. code-block:: bash

    git review 

Your change will now be visible on GerritHub for review. In order to amend your change after pushing it for review, you will need to create additional patchsets.

In order to create an additional patchset, modify your exisiting commit and push your new changes for review

.. code-block:: bash

    git commit --amend
    git review

An additional patchset will now appear on the original GerritHub change.

Work in Progress
~~~~~~~~~~~~~~~~
Uploading changes that are not yet complete is highly encouraged in order to receive early feedback from project maintainers and other contributors. To label your change as a work in progress, leave a code review of your own patchset with a vote of -1 and a comment indicating that your patchset is a work in progress.

Rebasing A Commit
~~~~~~~~~~~~~~~~~
If changes have occurred to the master branch since your local branch was last updated, you will need to rebase your commit with the new changes. 

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
Once a change is submitted to GerritHub, project maintainers and other contributors will review it and leave feedback. In order for a change to be merged, a change must have at least two +2 votes from project maintainers, and must pass all Jenkins continuous integration tests. 

Continuous Integration Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All patchsets submitted to the Armada GerritHub undergo continuous integration testing performed by Jenkins. If the Jenkins build is successful, Jenkins will leave a code review with a vote of +1. If the Jenkins build fails, Jenkins will leave a code review with a vote of -1.

In order to ensure that your patchset passes the continuous integration tests, from the root of the local repository, execute:

.. code-block:: bash

    nosetests -w armada/tests/unit --cover-package=armada --with-coverage --cover-tests

In order to ensure that your patchset conforms to the PEP8 style guide, from the root of the local repository, execute:

.. code-block:: bash

    flake8
