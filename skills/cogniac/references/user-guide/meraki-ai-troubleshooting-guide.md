# Meraki AI Troubleshooting Guide

## 1. Objective

This guide outlines the steps required to identify the possible reasons for not correctly operating Cisco Meraki MV series Smart Cameras, aiming to leverage video intelligence and the delivery of -powered computer vision applications at the edge of the network provided by Cogniac Corporation.

## 2. Common issues that indicate a failure

- My Camera is taking a long time for the initial setup
- Cameras can take up to 20 minutes ( if not longer) for first-time setup due to firmware upgrades, format/partitioning, and encrypting of the storage. They are sensitive to power and network fluctuations during this time. It is suggested to pre-stage cameras before deployment to avoid troubleshooting when cameras are less inaccessible.
- My camera is not online on the Cisco Meraki dashboard

If the camera goes offline and never checks back into the dashboard, please verify the following:

- Make sure the camera is powered ON. Refer to the section below for the troubleshooting flow.
- If the camera is powered ON:

  - Verify if the MV's IP address is ping-able via the LAN.
  - Verify the upstream switch-port configuration and fix any potential configuration issues.
  - MV's Dashboard connectivity traffic must be allowed upstream. Details are available at Help > Firewall Info.
  - Verify if the camera generates any traffic by running an upstream port capture.
  - If not, open a support ticket with Cisco Meraki to investigate further:

## Customer Support

Worldwide enterprise support: +1 (415) 937‑6671

European enterprise support: +44 203 808 7003

For more international dial-in numbers, visit the Meraki [support page](https://meraki.cisco.com/support)

Email: support@meraki.com

- Verify the successful hardware Installation of the Cisco Meraki MV camera setup.

The basic initial configuration of the second-generation cameras is just as simple as any other model of MV camera. The links below provide additional information and instructions for each step in getting the device set up and configured for the first time.

[Claim the device to an Organization on the Meraki Dashboard](https://documentation.meraki.com/General_Administration/Inventory_and_Devices/Using_the_Organization_Inventory) If a Dashboard Organization does not yet exist, [Create one](https://documentation.meraki.com/General_Administration/Organizations_and_Networks/Creating_a_Dashboard_Account_and_Organization)

[Add the device to a Dashboard Network](https://documentation.meraki.com/General_Administration/Inventory_and_Devices/Adding_and_Removing_Devices_from_Dashboard_Networks#Adding_Devices_to_Networks) If a Network does not yet exist, [Create one first](https://documentation.meraki.com/General_Administration/Organizations_and_Networks/Creating_and_Deleting_Dashboard_Networks#Creating_a_Network)

- Physically connect the device to the local network

  - Follow the steps in the corresponding [Installation Guide](https://documentation.meraki.com/MV/Physical_Installation)
  - Connect the device to any existing network infrastructure that provides PoE, DHCP, and Internet access
  - Boot the device and let it check into the Dashboard
  - Allow the device to completely check in and perform any initial firmware upgrades
  - Finish configuring the device from the Meraki Dashboard
  - Configure [Wireless Profiles](https://documentation.meraki.com/MV/Initial_Configuration/MV_Wireless_Configuration_Guide)
  - Configure [Privacy Windows](https://documentation.meraki.com/MV/Initial_Configuration/Privacy_Windows)
  - Configure Recording / Retention Settings

## At this stage, you should be able to access your Meraki cameras in your Meraki Dashboard:

- My Cisco Meraki MV cameras capture images, but they are not visible in the Cogniac CloudCore system?
- Check in the camera list if the camera is active (Green or Red status), and please check if the Meraki dashboard API key and Meraki API host are properly configured inside the Cognac CloudCore Tenant. Make sure you are a Tenant admin inside the Cogniac CloudCore system. Click under settings options in your upper right corner and select the option “Settings'. Scroll down and verify your Meraki dashboard API host and API key. The Meraki dashboard API is a software interface that interacts directly with the Meraki cloud platform and Meraki-managed devices. The dashboard API is an open-ended tool that can be used for many purposes. Here are some examples of how it is used today by Meraki customers:
- Add new devices, organizations, admins, networks, and VLANs
- What is a tenant? Please check: [here](/docs/tenant-home)
- My Tenant set with Meraki integration does not show the Meraki Camera Capture Application type inside Input/Output Applications inside Application Builder. This toolbox is on the left side of the CloudCore home page, and the Meraki AI Templates are not in the Cogniac CloudCore system. Why?
- Suppose you can not identify the Meraki Camera Application or Meraki AI Template inside the Application Builder(Home screen of the CloudCore system). In that case, you have to contact the Cogniac Service Delivery team for assistance in order to provide you access to those applications.
- My Tenant is set with Meraki integration. I Do see the Meraki Camera Capture Application type inside Input/Output Applications. But when I click on the Meraki Camera App button inside “Application Builder”, at the 2nd screen in the step-by-step procedure, more precisely at the screen named “Application Type Configuration”. I can not add a camera from the drop-down menu. Why?

  - Verify and check which of the Meraki Cameras inside your Cogniac CloudCore Tenant are free i.e., not already assigned/locked in another application. At this step, please identify a Meraki camera without any of the tags like “cogniac-box-xxxxxxxx”,cognac-capture-xxxxxxxx”
  - I created a Box Detection Application with 1x Meraki camera using the Meraki AI Template/Meraki Quick Start. Now, I want to add additional Meraki Camera(s). How Can I do this?
- Select the Box Detection Application you created and then click on the App Settings, then scroll down and Input Subject Section. Click on the Input Subject to add the new cameras to your Application. In the search box, type the serial number of your camera, MAC address, or name as per your Meraki Dashboard.
- Once the application is created, check if the Output Subject is properly created or if it exists. If the Output Subject is not visible, it was most possibly misconfigured during the application creation.
- Check once the App was created if the tags are correctly displayed (Meraki-App + 'camera ID')
- Check under Meraki Dashboard if the same tags are used for the cameras (meaning that the camera is already in use )
- I have a Box Detection application created with 2 Meraki cameras. Now, I want to remove 1xMeraki Camera from the Application pipeline. How Can I do this? Open your box detection application, click on App settings, scroll down, and in the “Input Subjects” section, you can see the already added cameras. Decide which camera/s to remove, and on the top right corner of the selected camera/s, you will see an “X”. Click on it, and the camera/s will be removed.
- I can not add new cameras to participate in my Box Detection Application as they direct downstream to my Application. Why? You should check the camera status - if another application already uses it, you won't be able to add it.
- I cannot delete the Meraki Capture Output subject associated with an active Meraki Capture Application. Why?
- I am running out of storage in my Meraki-enabled CloudCore tenant. How Can I Remediate this? You should contact us at support@cogniac.ai or set the ‘Media Expiration Time’
- How to change the ‘Media Expiration Time’ On your box detection application, click on the Output subject application, click on “Subject Settings”, scroll down, and in the “Advanced” section, you will be able to see “Media Expiration Time”. From the drop-down menu, select the option that you prefer.
- You have a Meraki-enabled CloudCore Tenant. You have a running Application pipeline with a Meraki Camera capture Application and a Box Detection Application. How can We check if a new Meraki custom model will automatically push new model releases to the associated Meraki cameras with the Box detection App? Open your box detection application, click on App settings, scroll down, and in the “Application Configuration” section, you will be able to see “ Meraki Model Push”. Set it to “True”.
- You have a Meraki-enabled CloudCore Tenant. You have a running Application pipeline with a Meraki Camera capture Application and a Box Detection Application. You must disable adding additional input subjects to the Box detention app. How Can you achieve this? Inside the Meraki camera application, you could disable adding new additional input subjects by deactivating the Meraki Application.
- Can We inject images from multiple Meraki cameras? Yes, You could inject images from multiple Meraki Cameras
- You are trying to add two Meraki camera capture applications that can share the same camera. Is this possible? No, one camera can downstream media only to a single application.
- How Can I verify that my camera is connected and set up to the Cogniac System? The camera should be visible upon creating the Meraki AI application and in green status, indicating it is online and available.
- How Can a user delete a Meraki Camera Capture application? To delete a Meraki Camera Capture App, we should first make the application inactive and then delete it.
- Application is not releasing a new model? Please refer to [Training & Feedback](/docs/tutorial-how-to-label-images-and-train-models) for details
- The images are blurry. Why is the app not releasing a new model with higher performance?

  It is important to be able to visually identify the object of interest without using other contextual information within the imagery or metadata.
- In the box detection app, why, after initial training, do I see training credit? What does it mean for me and the model? The training credits are used to help prioritize training. The higher the training credits, the more likely the application will be selected for additional training. Each training consumes 1 credit, but there is still always a chance that an application without training credits can be selected for training. The more feedback you provide, the more credits you earn (up to 50 per application).
- What are - FP(False Positive), FN(False Negative), TN(True Negative) & TP(True Positive), and how are they related to the performance? Please refer to [Model Performance](/docs/applications-model-performance)  for more information

## Network Troubleshooting Guide for Cisco Meraki Cameras

Basic Troubleshooting Tasks and Startup Issues:

This action describes the basic procedures users should perform before undertaking a detailed troubleshooting analysis of the Cisco Meraki MVSeries Security Cameras.

****Basic Troubleshooting checklist****

If you encounter a problem after you install the Cisco Meraki MV camera, go through the following troubleshooting checklist to check for the most common error conditions before you contact the Cogniac Technical Support Center or before you perform a detailed troubleshooting analysis:

- Are all data cables firmly connected at both ends?
- Is the port adequately configured?

  1. Please double-check that the duplex and speed settings are properly configured on both sides of the LAN connection between Meraki MV Camera and the switch residing in the same broadcast domain. By default, Cisco switches will auto-negotiate the speed and duplex settings. Check the 1x 10/100/1000BASE-T Ethernet (RJ45) port
  2. Confirm the device is establishing a link with the upstream switch
  3. Make sure layer 1 connectivity is healthy
- Check if the LED on the Ethernet port is lit or seen as a mesh neighbor
- Check if the device has connectivity to the local router connected to a working internet connection and all the cases below:

  1. Check if the device is reachable inside your LAN.Use the ping command that will help you determine connectivity between devices on your local area network.
  2. Launch a ping command from your local managed switch to the IP of the Meraki MV Camera. If it is reachable, launch a ping against the IP address of the Meraki device from your local gateway/router. If it’s reachable, there are no issues inside your local network.
  3. If your Meraki device is not reachable from your LAN switch, verify the upstream switch-port configuration and fix any potential configuration issues.
  4. A properly working internet connection will have access to the IP addresses, ports, and protocols defined for establishing TCP and UDP connections from the Meraki cameras to the Meraki Dashboard and vice versa. Please consider the following firewall rules to be enabled on your Firewall or Router facing the internet.

![](../../../assets/media/images/meraki-ai-troubleshooting-guide-2023-image-satkb1fs.png)

- A packet filter or firewall might prevent traffic from passing through an IP address or protocol.
- Is the device receiving an IP address from the local DHCP server, or is a valid static IP adequately assigned?
- Taking a packet capture on the router's interface facing the local network and downloading the .pcap file is recommended if your Meraki Camera(s) has not been checked inside the Meraki Dashboard. Thus, network troubleshooting will make it much easier to pinpoint the root cause of the network failure to establish a connection between the Meraki cameras installed at your sites and the Dashboard of the Meraki cloud-based management system.
- Disable flow control on all your switch ports. Flow Control is a predictive congestion management technology. It is used by a switch or client/server to prevent uncontrolled packet drops. When the switch or server PREDICTS that based on the current traffic flow, it will run out of buffers in the following few packets, sending a PAUSE frame (request) at the sending device. Upon receipt of the PAUSE frame, assuming the sending device is configured to respond to pause requests, the transmitting device will stop sending traffic for a few milliseconds. The faster the link speed, the shorter the duration of the pause. This is a complete freeze of all traffic flow, indiscriminate of traffic priorities.
- Consider implementing QoS inside your network trust boundary.
- Consider adding rules to grant access to the following outbound destination nets on port UDP 7351 on your firewall/router ACLs. These ACL rules define network communication from your local network to the destination networks at the Meraki Dashboard, directing the outbound traffic to them. The purpose of the communication is Meraki cloud communication:

  1. 209.206.48.0/20 UDP 7351
  2. 216.157.128.0/20 UDP 7351
  3. 158.115.128.0/19 UDP 7351
  4. 64.62.142.12/32 UDP 7351
- Consider adding rules to grant access to the following outbound destination nets on port TCP 443 on your firewall/router ACLs. These ACL rules define network communication from your local network to the destination networks at the Meraki Dashboard, directing outbound traffic to them. The purpose of the communication is Meraki cloud communication:

  1. 209.206.48.0/20 TCP 443
  2. 216.157.128.0/20 TCP 443
  3. 158.115.128.0/19 TCP 443
- Consider adding rules to grant access to the following outbound destination nets on port TCP 443 on your firewall/router ACLs. These ACL rules define network communication from your local network to the destination networks at the Meraki Dashboard, directing outbound traffic to them. The purpose of the communication is to Backup Meraki cloud communication, Backup configuration downloads, Measured throughput to dashboard.meraki.com, and Backup firmware downloads:

  1. 209.206.48.0/20 TCP 80
  2. 216.157.128.0/20 TCP 80
  3. 158.115.128.0/19 TCP 80
  4. 209.206.48.0/20 TCP 7734
  5. 216.157.128.0/20 TCP 7734
  6. 158.115.128.0/19 TCP 7734
  7. 209.206.48.0/20 TCP 7752
  8. 216.157.128.0/20 TCP 7752
  9. 158.115.128.0/19 TCP 7752
- Performance Testing of network throughput by using the extended ping command. The extended ping performs a more advanced check of host reachability and network connectivity. You can obtain the round-trip time (RTT) with the ****ping****and ****traceroute****commands. This is the time required to send an echo packet and get a response. This can provide a rough idea of the delay on the link. However, these figures are not precise enough for performance evaluation.

Example of using extended ping to check the connectivity, round trip time, and packet loss inside the local network where the Cisco Meraki MV cameras are located:

router#****ping****

Protocol [ip]:

Target IP address: 192.168.100.200

Repeat count [5]: 110<<<<<<< this means run the sweep one hundred and ten times

Datagram size [1500]: ****Size of the ping packet (in bytes). Default: 100 bytes****.

Timeout in seconds [2]:

Extended commands [n]:

Sweep range of sizes [n]: n

Type escape sequence to abort.

Sending 110, [1500]-byte ICMP Echos to 192.168.100.200 Timeout is 2 seconds:

<<<<<<< This means the result is 110 packets ( 1500 bytes)

The success rate is 100 percent (110/110), round-trip min/avg/max = 8/9/12 ms.

- I am using curl to make an API call to the Meraki Dashboard to verify that a Meraki device has checked in the Meraki Dashboard. The Meraki Dashboard API requires a header parameter of “X-Cisco-Meraki-API-Key” to authorize each request.

****Returns the identity of the current user****

****Launch an API call against the Meraki Dashboard in order to check your identity in the Dashboard****

****curl '****[****https://api.meraki.com/api/v1/administered/identities/me****](https://api.meraki.com/api/v1/administered/identities/me)****' \****

****-H 'X-Cisco-Meraki-API-Key: {MERAKI-API-KEY}'****

****Find your Organisation ID****

To begin navigating the API, you must first know your organization ID. This will be required for endpoints needing an organizationId parameter.

****curl**** https://api.meraki.com/api/v1/organizations****\****

****-L -H 'X-Cisco-Meraki-API-Key: {MERAKI-API-KEY}'****

****Find your network ID****

Now that you have an organization ID, list the networks of the organization

curl https://api.meraki.com/api/v1/organizations/{organizationId}/networks \

-L -H 'X-Cisco-Meraki-API-Key: {MERAKI-API-KEY}'

****Find your Device Serials****

Use the ID from the ~/networks response as the networkId in the following request.

curl https://api.meraki.com/api/v1/networks/{networkId}/devices \

-L -H 'X-Cisco-Meraki-API-Key: {MERAKI-API-KEY}'

==============================================================
