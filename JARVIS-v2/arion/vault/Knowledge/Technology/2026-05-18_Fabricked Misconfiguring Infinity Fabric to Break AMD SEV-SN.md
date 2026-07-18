---
title: "Fabricked: Misconfiguring Infinity Fabric to Break AMD SEV-SNP"
source: https://xca-attacks.github.io/fabricked/
date: 2026-05-18
tags:
  - news
  - auto-learning
  - auto-injected
---

# Fabricked: Misconfiguring Infinity Fabric to Break AMD SEV-SNP

On this page
Summary
Confidential computing allows cloud tenants to offload sensitive computations and data to remote resources without needing to trust the cloud service provider. Hardware-based trusted execution environments, like AMD SEV-SNP, achieve this by creating Confidential Virtual Machines (CVMs). With Fabricked, we present a novel software-based attack that manipulates memory routing to compromise AMD SEV-SNP. By redirecting memory transactions, a malicious hypervisor can deceive the secure co-processor (PSP) into improperly initializing SEV-SNP. This enables the attacker to perform arbitrary read and write accesses within the CVM address space, thus breaking SEV-SNP core security guarantees.
What is AMD SEV-SNP?
Standard cloud environments expose tenant computation and data in use to potentially untrusted cloud service providers. Confidential computing addresses this by using Confidential Virtual Machines (CVMs): hardware-shielded environments that isolate active workloads and guarantee complete data privacy from the host. Secure Encrypted Virtualization-Secure Nested Paging (SEV-SNP) is an AMD hardware extension that enables CVMs on AMD server CPUs.
What is the Infinity Fabric?
Modern AMD System-on-Chips (SoCs) use a chiplet-based architecture. The core idea is to manufacture individual CPU blocks on separate dies and link them together via a high-speed interconnect. While this design significantly improves manufacturing yields, it also introduces complexity in inter-component communication. AMD addresses this with the Infinity Fabric, which is responsible for coherent data transport, memory routing, and address mapping across CPU cores, memory controllers, and peripheral devices. Because platform configurations vary between different systems and boot sequences, the Infinity Fabric must be dynamically configured during every CPU boot sequence. AMD delegates parts of this configuration process to the motherboard firmware, also known as BIOS or UEFI.
Fabricked Overview
In the confidential computing threat model, the UEFI is untrusted and cloud-provider-controlled. In Fabricked, we first identify that the untrusted UEFI is in charge of locking down parts of the Infinity Fabric configuration. As an attacker, we modify the UEFI to skip these API calls. This leaves the Infinity Fabric configurable by the attacker even after SEV-SNP is activated on the machine.
The attacker, i.e., a malicious hypervisor, can therefore modify the Infinity Fabric to re-route DRAM memory transactions. Since the Infinity Fabric connects not only the CPU cores but also the secure co-processor (PSP) to the DRAM, we can manipulate PSP read/write operations to DRAM. We use this attacker capability to compromise SEV-SNP initialization. Specifically, we identify that during the SEV-SNP initialization, the PSP sets up a critical data structure, the RMP, that enforces memory access control rules to CVM memory. During this setup, the PSP has to perform memory writes to the DRAM. By misconfiguring the Infinity Fabric before these PSP writes, we are able to drop them. This results in an uninitialized RMP, i.e., it remains completely unchanged, retaining its insecure default entries set up by the malicious hypervisor. In other words, by using Fabricked, the attacker bypasses parts of the SEV-SNP initialization while tricking it into believing it succeeded. When the victim launches CVMs subsequently on the platform, the hypervisor can access their memory as the RMP enforcement is useless for all practical purposes.
What went wrong?
Fabricked is possible due to two critical flaws. First, the hypervisor can maliciously corrupt some Infinity Fabric routing rules. Second, when the security co-processor subsequently issues memory requests, the corrupted routing rules take precedence over the correct ones — silently misdirecting writes that should have initialized the RMP.
Attack Complexity
Fabricked operates as a fully deterministic, software-only exploit with a 100% success probability. It does not depend on any code running inside the victim CVM and requires no physical access to the hardware.
Affected Hardware
We confirmed the vulnerability on AMD Zen 5 EPYC processors running SEV-SNP. However, the AMD advisory also lists firmware updates for Zen 3 and Zen 4 processors. We note that the patchnotes for these systems also list CVE-2025-54510 mitigations. Therefore, we assume Fabricked affects Zen 3, Zen 4, and Zen 5.
FAQ
Q: Does this attack have implications beyond SEV-SNP?
- Fabricked misroutes memory accesses of the AMD on-chip security co-processor, the PSP. We have not studied the impact of the vulnerability beyond SEV-SNP.
Q: Does Fabricked affect non-confidential VMs that I have in the cloud?
- No. Fabricked assumes a malicious hypervisor and UEFI to reconfigure the Infinity Fabric. In the non-confidential VM threat model, the hypervisor and the UEFI are considered trusted.
Q: What are the requirements for the attack?
- An attacker 

---
*Synthesized by AutonomousLearner*
