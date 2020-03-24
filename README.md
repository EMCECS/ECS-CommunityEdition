# ECS Community Edition

**ECS CE Install Node Image**
[![](https://images.microbadger.com/badges/version/emccorp/ecs-install.svg)](https://microbadger.com/images/emccorp/ecs-install "Get your own version badge on microbadger.com")

**ECS Software Image**
[![](https://images.microbadger.com/badges/version/emccorp/ecs-software-3.5.0.svg)](https://microbadger.com/images/emccorp/ecs-software-3.5.0 "Get your own version badge on microbadger.com")

Current releases and history are available [here][releases].

## Community Guides
Please read our [Community Code of Conduct][ccoc] before contributing.  Thank you.


## Description

EMC ECS is a stateful, containerized, object storage system for cloud storage protocols.  ECS is compatible with AWS S3 and OpenStack Swift.  On file-enabled buckets, ECS can provide NFS exports for file-level access to objects.

ECS can be set up on one or more hosts or virtual machines in a single-site or a multi-site geo replicated configuration. We want the wider community to use ECS and provide feedback.  Usage of this software is under the End User License Agreement at the bottom of this README.

ECS Community Edition is a free, reduced footprint, version of Dell EMC's ECS software. Of course, this means there are some limitations to the use of the software, so the question arises; how is the Community Edition of ECS different from the production version?

### License difference
As noted with the included license, ECS Community cannot be used in production environments and is intended to be used for trial and proof of concept purposes only. This software is still owned and protected by Dell EMC.

### Feature differences
It it important to note that ECS-Community Edition is ***not*** the same as ECS software and as such lacks some features that are integral to the actual ECS software.

* **ECS Community Edition does NOT support encryption**
* **ECS Community Edition does NOT include ECS' system management, or "fabric", layer**

### Notice
Because of these differences, ECS Community Edition is absolutely **not** qualified for testing failure scenarios. Failure scenarios can only be adequately mimicked on the full version of ECS Software.


## Quick Start Guide
If you have the following:

1. A CentOS *Minimal* install of the latest CentOS release with:
    1. 16GB RAM
    2. 16GB block device for system
    3. 104GB block device for ECS
2. Internet access
3. No proxies, local mirrors, or special Docker registries

Then you should be able to get up and going with a Single-Node All-in-One install using these commands on your VM:

```
# git clone https://github.com/EMCECS/ECS-CommunityEdition
# cd ECS-CommunityEdition
# cp docs/design/reference.deploy.yml deploy.yml
# echo "Edit this deploy.yml to match your VM's environment"
# vi deploy.yml
# ./bootstrap.sh -y -g -c deploy.yml
```

And then after the node reboots (you did use a clean minimal install from ISO or netinstall right?):

```
# step1
# step2
```

And if all went well, you now have a working stand-alone ECS, mostly configured, and ready for use.

## Hardware Requirements

### Minimum
_Note: A minimum configuration is only suitable for short-term sandbox testing_
Hardware or virtual machine with:

* 4 CPU Cores
* 16GB RAM
* 16GB root block storage
* 104GB additional block storage
* CentOS Minimal installation of the latest CentOS release

### Recommended
_Note: A recommended configuration is more suitable for longer-term functional testing_
Hardware or virtual machine with:

* 8 CPU Cores
* 64GB RAM
* 16GB root block storage
* 1TB additional block storage
* CentOS Minimal installation of the latest CentOS release

## Deployment Scenarios
### Deploy into Internet-Connected Environments

#### [ECS Single-Node All-in-One Deployment (recommended, fastest, smallest footprint)](docs/source/installation/ECS-Installation.md)
Deploy a stand-alone instance of ECS to a single hardware or virtual machine.

#### [ECS Multi-Node All-in-One Deployment with Install Node (EC replication with > 3 nodes)](docs/source/installation/ECS-Installation.md)
Deploy a multi-node ECS instance to two or more hardware or virtual machines.  Three nodes are required to enable erasure-coding replication.

### Deployments into Soft-Isolated and Air-Gapped Island Environments
##### Important information regarding Island deployments
Please be aware that install node bootstrapping requires Internet access to the hardware or virtual machine that will become the install node, but once this step is complete, the machine can be removed from the Internet and migrated into the Island environment.

#### Deploying from OVA
In situations where Internet access is completely disallowed, or for the sake of convenience, an OVA of a prefabricated, bootstrapped, install node is provided.  Please download the OVA from one of the links below.

The OVA is shipped as a bootstrapped install node.  It must be cloned multiple times to create as many Data Store Nodes as desired.

###### OVA Special Requirements
* All nodes **MUST** be clones of the OVA.
* All nodes **MUST** have their virtual hardware configurations updated to match the node type requirements.
###### Default Credentials
* The default password for the `admin` accounts is `ChangeMe`. The default password for `root` is unknowable.
###### Network Configuration
* The OVA is configured to acquire network settings via DHCP.  Static configurations must be manually configured with `sudo nmtui`

##### OVA Download Links
Please see the [release page](https://github.com/EMCECS/ECS-CommunityEdition/releases) for OVA download links.

#### [ECS Single-Node Deployment with Install Node (recommended)](docs/source/installation/ECS-Installation.md)
Using an install node for isolated environments, deploy a stand-alone instance of ECS to a single hardware or virtual machine.

#### [ECS Multi-Node Deployment with Install Node](docs/source/installation/ECS-Installation.md)
Using an install node for isolated environments, deploy a multi-node ECS instance to two or more hardware or virtual machines.  Three nodes are required to enable erasure-coding replication.


# Directory Structure

|   Directory Name   |   Description   |
|--------------|-----------|
| [docs](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/docs) | Documentation sources; [read them online at Read the Docs](http://ecsce.readthedocs.io/en/latest/)
| [examples](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/examples) | Deployment and configuration examples for common scenarios
| [contrib](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/contrib) | Unsupported community-contributed scripts content related to ECS CE
| [patches](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/patches) | Patches to the ECS Community Edition Docker image
| [bootstrap.sh](https://github.com/EMCECS/ECS-CommunityEdition/blob/develop/bootstrap.sh) | Install Node bootstrap script
| [release.conf](https://github.com/EMCECS/ECS-CommunityEdition/blob/develop/release.conf) | Installer release information file
| [ui](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/ui) | Install Node utilities and support files
| [bootstrap_plugins](https://github.com/EMCECS/ECS-CommunityEdition/tree/develop/bootstrap_plugins) | Install Node bootstrap script support files


# Support

Please file bugs and issues at the [ECS's site in the EMC Community Network (ECS's support site) ](https://community.emc.com/community/products/ecs) and you can also use this GitHub's repository issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stack Overflow</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.

# License Agreement

## EMC ECS Software Limited-Use License Agreement

This EMC Software License Agreement (the "Agreement") is a legal agreement between EMC Corporation, with a principal office at 176 South Street, Hopkinton, MA 01748 USA ("EMC") and you and the organization on whose behalf you are accessing this Agreement (the "Customer") and governs Customer’s access to, downloading of, and use of any and all components, associated media, printed materials, documentation, and programming accessed via the EMC software (the "Software").

By clicking on the "Agree" or check box or similar button set forth below, or by downloading, installing, or using the Software, you are representing to EMC that (i) you are authorized to legally bind the Customer, and (ii) you are agreeing on behalf of the Customer that the terms of this Agreement shall govern the relationship of the parties with regard to the Software.

If you do not have authority to agree to the terms of this Agreement, or do not accept the terms of this Agreement, click on the "Cancel" or similar button or discontinue your efforts to download the Software, and the registration, download and/or installation process will not continue. In such event, no access to, or authorization to download or use the Software, is granted by EMC.

EMC and Customer enter into this Agreement and this Agreement shall become effective on the date on which Customer clicks on the "Agree" button described above or downloads, installs or uses the Software, whichever occurs first (the "Effective Date"). NOW, THEREFORE, in consideration of the premises and obligations contained herein, it is agreed as follows:

### 1.0 - DEFINITIONS

**1.1** - "Equipment" means the Customer owned storage devices, systems, or central processing units that the Software was designed to run on or with.

**1.2** - "Software" means the free EMC Software made available for download by Customer from a designated EMC web site.

### 2.0 - PURPOSE AND SCOPE

**2.1** - The Software shall be used for Customer’s internal business purposes and in accordance with EMC’s instructions and documentation. The Software is available from EMC to Customer at no charge, but only after Customer agrees to the license terms as contained in this Agreement.

**2.2** - Under this Agreement, Customer may use the Software on the related Equipment it owns.

### 3.0 LICENSE TERMS

**3.1** - EMC grants Customer a license to use the Software on the Equipment commencing on download for as long as Customer complies with this Agreement. The foregoing licenses shall be non-exclusive, non-transferable, and non-sublicensable and subject to the restriction that the Software be used solely on or in connection with the Equipment for which it was licensed. EMC may terminate licenses, without liability, if Customer breaches this Agreement and fails to cure within thirty (30) days after receipt of EMC’s written notice thereof. Upon termination, Customer shall cease all use and return or certify destruction of Software (including copies) to EMC. Customer shall not, without EMC's prior written consent, use the Software in a production environment, service bureau capacity, or copy, provide, disclose or otherwise make available Software in any form to anyone other than Customer's agents, employees, consultants or independent contractors ("Personnel"), who shall use Software solely for Customer's internal business purposes in a manner consistent with this Agreement. Customer shall be fully responsible to EMC for the compliance of Customer’s personnel herewith.

**3.2** - Software is licensed only. No title to, or ownership of, the Software is transferred to Customer. Customer shall reproduce and include copyright and other proprietary notices on and in any copies, including but not limited to partial, physical or electronic copies, of the Software. Neither Customer nor its personnel shall modify, enhance, supplement, create derivative works from, reverse assemble, reverse engineer, reverse compile or otherwise reduce to human readable form the Software without EMC's prior written consent. Any third party software that may be provided by EMC shall be governed by the third party’s separate license terms, if any.

### 4.0 - DELIVERY AND INSTALLATION

**4.1** - Delivery of the Software is by download only.

**4.2** - EMC shall, as necessary, provide Customer with information to download, install and use the Software.

### 5.0 - TERM AND TERMINATION

**5.1** - If Customer fails to perform any of its material covenants, obligations or responsibilities under this Agreement, Customer shall be in default and breach of this Agreement, and EMC shall, in addition to any other remedies, which may be available to EMC under this Agreement, in law or equity, in its sole discretion, have the right to terminate this Agreement and any or all related license(s) granted to Customer by written notice thereto, with such termination to be effective immediately.

**5.2** - EMC may terminate this Agreement for its convenience at any time by providing Customer with a minimum of thirty (30) days prior notice.

### 6.0 - NO WARRANTY OR SUPPORT

**6.1** - EMC PROVIDES ALL SOFTWARE HEREUNDER ON AN "AS-IS," "WHERE IS" BASIS, AND MAKES NO OTHER EXPRESS WARRANTIES, WRITTEN OR ORAL, AND ALL OTHER WARRANTIES ARE SPECIFICALLY EXCLUDED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NON-INFRINGEMENT, AND ANY WARRANTY ARISING BY STATUTE, OPERATION OF LAW, COURSE OF DEALING OR PERFORMANCE, OR USAGE OF TRADE.

**6.2** - EMC shall not provide any technical support, SLA’s, telephone support, on-line support, or support of any kind under this Agreement. Customer is not entitled to receive any updates, upgrades or enhancements of any kind under this Agreement. This includes, but is not limited to, security vulnerabilities that may be applicable to the Software.

**6.3** - No representation or other affirmation of fact, including but not limited to statement regarding capacity, suitability for use or performance of Software, whether made by EMC employees or otherwise, shall be deemed to be a warranty for any purpose or give rise to any liability of EMC whatsoever unless contained in this Agreement.

### 7.0 NO INDEMNIFICATION

**7.1** - EMC shall have no liability to Customer for any action (and all prior related claims) brought by or against Customer alleging that Customer’s use or other disposition of any Software infringes any patent, copyright, trade secret or other intellectual property right. In event of such an action, EMC retains the right to terminate this Agreement and take possession of the Software.

**7.2** - THIS SECTION 7.0 STATES EMC’S ENTIRE LIABILITY WITH RESPECT TO ALLEGED INFRINGEMENTS OF INTELLECTUAL PROPERTY RIGHTS BY THE SOFTWARE OR ANY PART OF THEM OR BY ITS OPERATION.

### 8.0 LIMITATION OF LIABILITY

**8.1** - EMC’S AND ITS SUPPLIER’S TOTAL LIABILITY AND CUSTOMER’S SOLE AND EXCLUSIVE REMEDY FOR A CLAIM OF DAMAGE TO REAL OR TANGIBLE PERSONAL PROPERTY OR ANY OTHER CLAIM WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS BASED ON CONTRACT, WARRANTY, NEGLIGENCE OR STRICT LIABILITY IN TORT, THAT ARISES OUT OF OR IN CONNECTION WITH SOFTWARE OR SERVICES PROVIDED HEREUNDER, SHALL BE LIMITED TO PROVEN DIRECT DAMAGES CAUSED BY EMC’S SOLE NEGLIGENCE IN AN AMOUNT NOT TO EXCEED US$5,000. IN NO EVENT SHALL EMC OR ITS SUPPLIERS BE LIABLE FOR CONSEQUENTIAL, INCIDENTAL, INDIRECT, OR SPECIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, LOSS OF PROFITS, REVENUES, DATA AND/OR USE) EVEN IF ADVISED OF THE POSSIBILITY THEREOF. NEITHER PARTY SHALL BRING ANY CLAIM ARISING OUT OF THE SOFTWARE OR SERVICES PROVIDED HEREUNDER MORE THAN EIGHTEEN (18) MONTHS AFTER SUCH CLAIM HAS ACCRUED.

**8.2** - IF CUSTOMER USES SOFTWARE FOR ANY PURPOSE EXCEPT AS STATED HEREIN OR OTHERWISE AGREED IN WRITING, EMC SHALL HAVE NO LIABILITY WHATSOEVER FOR ANY DAMAGE TO EQUIPMENT OR DATA, OR FINANCIAL LOSSES, RESULTING FROM SUCH USE.

### 9.0 GENERAL

**9.1 - Assignment** – Customer shall not assign any right or interest hereunder nor delegate any work or other obligation to be performed hereunder to any entity other than its corporate parent, or a division or wholly or majority owned subsidiary of the party or its corporate parent. Any such action in violation of the foregoing shall be void.

**9.2 - Entire Agreement** - The terms contained herein constitute the entire agreement between the parties with respect to the subject matter hereof and shall supersede all prior communications and agreements, either oral, written or otherwise recorded.

**9.3 - Compliance with Export Control Laws** – Customer shall comply with all applicable export laws, orders and regulations and obtain all necessary governmental permits, licenses and clearances.

**9.4 - Governing Law** - This Agreement shall be governed by the laws of the Commonwealth of Massachusetts, excluding its conflict of law rules. The U. N. Convention on Contracts for the International Sale of Goods shall not apply.

**9.5 - Notices** – Except for routine communications, all other notices required or permitted hereunder, including but not limited to notices of default or breach, shall be signed by an authorized representative of the sender. Such notices shall be deemed to have been received (i) when hand delivered to such individuals by a representative of the sender; (ii) three (3) days after having been sent postage prepaid, by registered or certified first class mail, return receipt requested; (iii) when sent by electronic transmission, with written confirmation by the method of transmission; or (iv) one (1) day after deposit with an overnight carrier, with written verification of delivery.

**9.6 - No Waiver** – No omission or delay by either party in requiring the other party to fulfill its obligations hereunder shall be deemed to constitute a waiver of (i) the right to require the fulfillment of any other obligation hereunder; or (ii) any remedy that may be available hereunder.

**9.7 - Independent Contractors** - The parties shall act as independent contractors for all purposes under this Agreement. Nothing contained herein shall be deemed to constitute either party as an agent or representative of the other party, or both parties as joint venturers or partners for any purpose. Neither party shall be responsible for the acts or omissions of the other party, and neither party will have authority to speak for, represent or obligate the other party in any way without an authenticated record indicating the prior approval of the other party.

**9.8 - Separability** - If any provision of this Agreement shall be held illegal or unenforceable, such provision shall be deemed separable from, and shall in no way affect or impair the validity or enforceability of, the remaining provisions.

[ccoc]: https://github.com/EMCECS/ECS-CommunityEdition/blob/master/CODE_OF_CONDUCT.md
[contributing]: https://github.com/EMCECS/ECS-CommunityEdition/blob/master/.github/CONTRIBUTING.md
[releases]: https://github.com/EMCECS/ECS-CommunityEdition/releases
[legacy_changelog]: https://github.com/EMCECS/ECS-CommunityEdition/blob/master/docs/legacy/changelog.md
