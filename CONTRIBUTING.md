# Pull requests

When contributing make pull requests to the feature branch for the next release, don't commit to master branch 
If you want to contribute feel free to request new features, check first TODO.

# Help

 Check the [Flowchart](picts/flow_chart) to get a bettter understanding of the driver internals, pictures starting with **one-** ex. [one-deploy.png](picts/flow_chart/one-deploy.png) ressemble the scripts overview. The action scripts are written in python, there is a script  [lxd_common.py](src/remotes/vmm/lxd/lxd_common.py) containing lots of functions used by the action scripts ex. [lxd_common.py](src/remotes/vmm/lxd/deploy.py) which is executed when starting a VM, tus reducing the code, if you want to add code and it could be used by several action scripts then add it here.

# License and copyright

By default, any contribution to this project is made under the Apache
2.0 license.

The author of a change remains the copyright holder of their code
(no copyright assignment).