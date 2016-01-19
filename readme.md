# Undelayed forwarding in Software Defined Networks.

## How to use?

At first clone repository to your local disc.

Because project is based on Vagrant-provided Ubuntu virtual machine, you must install Vagrant.
After that, on host machine, go to *Vagrant-box/* folder and run VM by command **vagrant up**.
At first time it can take a while.
When your VM will be ready, you can establish SSH connection by command **vagrant ssh**.
You will need two separate SSH sessions (or use unix **screen** program).

In first SSH session go to the folder *~/dmas/* and execute command **python ./runner.py**.
You can read help for runner by executing **python ./runner.py -h**.
For development purposes it is convenient to use remote controller instead of controller run by runner, so do not provide *-c* parameter
(if controller is started by runner, there is no option to see controller logs which are extremely useful during development).

If you do not provide *-c* parameter for runner, in second SSH session go to the folder *~/pox/* and execute command **python ./pox.py MODULE_NAME**.
MODULE_NAME can be any Python file located in folder *~/dmas/pox/ext/* but with stripped *.py* extension.

Now you have working topology with controller logging to the screen any ipv4 message sent between hosts.
You can write your own Python client-server that will be simulating flow of packets described in your task.

## Problem:

Classical enterprise topology could look like this:

INTERNET (HOST) <-> GATEWAY/FIREWALL <-> SWITCH <-> SWITCH <-> ... <-> SWITCH <-> HOST

The problem is gateway/firewall where inspection of different types are performed (spam classification, web-browser analysis, mail attachment scaning), and after successful inspection, the packet is forwarded.

This is the place where SDN (Software Defined Network) comes in place. Our topology with SDN will look exactly the same, with the difference that each network device (firwall, switch, router) will be controlled by the some kind of server (controller) and have overall visibility of the whole topology. And could steer each device with knowledge of the other networking device state.

## Step 1

Implement simple topology as presented above with SDN simulator : mininet (VM with mininet is downloadable from Internet).
Create topology with gateway and multiple switches  (how many is not really important as beginning - after obtaining first results we will modify - probably add another switches between) controlled by controller (for example POX controller downloadable from github). Using POX steer gateway to perform classification and steer switch to forward packet to proper destination host.
The first step will be to test how much time does standard way (described in previous sentence) will need to perform classification/inspection and then if success - forwarding.

1. Packet income to gateway.
2. Controller steering gateway are making inspection.
  1. If ok, controller inform gateway and other switches to forward data to destination.
  2. If not ok, controller will drop packet on gateway.

## Step 2

The second step will be to reprogram controller to allow forwarding traffic to destination, however parallel performing proper inspection and of course not allowing packet to be forwarded to destination by the last switch without the result of inspection. The simple workflow would look like this:

1. Packet income to gateway
2. Data are inspected on controller using dedicated software while being forwarded to the next stop.
  1. If forwarded to inter-networking switch (not on the edge of topology) and no blocking message from controller, forward to the next switch (controller must send message to this switch to inform it to send it further also).
  2. If forwarded to inter-networking switch (not on the edge of topology) but controller inspects data and it is was classified for example as a spam, sends already blocking message to switch, drop packet.
  3. If forwarded to edge switch (right before final destination), switch waits for decision:
    * if controller hasn't finished inspection default action applied by controller on the edge switch should be wait (add to queue).
    * if controller has finished and is ok - controller apply action to forward data to destination.
    * if controller has finished and is not ok - controller of course should send dropping action to edge switch.

Parallel to 2.1 action there should be action performed on controller:
  1. Applying all internetworking switches forwarding action. Applying edge switch wait action. Inspecting data against proper case.
  2. If inspection completed and ok - controller apply action to forward data to destination on the edge switch.
  3. If inspection completed and not ok - controller apply action to drop data on the edge switch.

Hopefully controller finishes inspection before packet reaches edge device, however I predict all packets will land in queue, however total time while forwarding on switches and parallel inspection should be (by logic) less then the time in the standard way with queueing on gateway.

## Groups

The 3 groups you divide will need to check this using mentioned inspection algoritms (of course in both scenarios the same soft should be used):

* 1st group - spam classification (controller should use some open-source mechanism to classify spam)
* 2nd group - web page analysis and blocking when classified as for example not suitable for children (for example using forbidden phrases on the site to classify it)
* 3rd group - mail attachment scaning (controller should use some open-source mechanism to scan attachments)

### Mail scanning 

The open-source mechanism chosen for mail scanning is **clamav** which is an open source standard for mail gateway scanning sfotware. 
It's installation has been added to the initalizaiton process of vagrant (**vagrant up**), when the machine is created. 
It has been configure to listen on the port 3310

## Links, guides:
- http://mininet.org/walkthrough/ Installation of mininet guide.
- https://github.com/mininet/openflow-tutorial/wiki Complete guide - how to create topology, how to clone, install, program controller (most examples are for Pox) to perform switching action, router action, firewall action and links for further analysis.
