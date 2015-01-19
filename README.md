
How to use it
=============

This is an example of using Ansible with [Online Labs](http://labs.online.net) it comes with a custom [dynamic inventory](https://github.com/achamo/ocs_ansible).

I recommand you to use it inside a virtualenv (and I assume you already have ansible)

	git clone https://github.com/achamo/ocs_provision_ansible.git
	cd ocs_provision_ansible
	virtualenv .
	source bin/activate
	pip install git+https://github.com/achamo/ocs_ansible.git
	export OCS_TOKEN="<API_TOKEN>"
	ansible-playbook -i production provision.yml


You can tune provision parameters in *roles/ocs/tasks/main.yml* :

* name
* image
* how many instances you want to run


