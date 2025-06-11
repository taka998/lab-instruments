# IEEE 488.2 Common Commands

\*CLS

The Clear Status (CLS) command clears the status byte by emptying the error queue and clearing all the event registers including the Data Questionable Event Register, the Standard Event Status Register, the Standard Operation Status Register and any other registers that are summarized in the status byte.

\*ESE <data>

Selects the desired bits from the standard event status enable register. The variable <data> represents the sum of the bits that will be enabled.

This register monitors I/O errors and synchronization conditions such as operation complete, request control, query error, device dependent error, status execution error, command error and power on. The selected bits are OR’d to become a summary bit (bit 5) in the byte register which can be queried. The setting by this command is not affected by the PXB preset or \*RST. However, cycling the PXB power or executing the command :STATus:PRESet will reset this register to zero.

Range: 0-255

\*ESE?

The Standard Event Status Enable (ESE) query returns the value of the Standard Event Status Enable Register.

\*ESR?

The Standard Event Status Register (ESR) query returns the value of the Standard Event Status Register.

\*IDN?

The Identification (IDN) query outputs an identifying string. The response will show the following information:

<company name>, <model number>, <serial number>, <firmware revision>

\*OPC

The Operation Complete (OPC) command sets bit 0 in the Standard Event Status Register when all pending operations have finished.

\*OPC?

The Operation Complete (OPC) query returns the ASCII character 1 in the Standard Event Status Register when all pending operations have finished.

This query stops any new commands from being processed until the current processing is complete. This command blocks the controller until all operations are complete (i.e. the timeout setting should be longer than the longest sweep).

\*OPT?

The options (OPT) query returns a comma-separated list of all of the instrument options currently installed on the signal generator.

\*PSC ON|OFF|1|0

The Power-On Status Clear (PSC) command controls the automatic power-on clearing of the Service Request Enable Register, the Standard Event Status Enable Register, and device-specific event enable registers.

| ON(1) | This choice enables the power-on clearing of the listed registers. |
| --- | --- |
| OFF(0) | This choice disables the clearing of the listed registers and they retain their status when a power-on condition occurs. |

\*PSC?

The Power-On Status Clear (PSC) query returns the flag setting as enabled by the \*PSC command.

\*RCL "<filename>"

The recall command recalls a configuration from a saved file that contains channel settings, configuration settings, and external instrument information. When the file is recalled, it updates the PXB application with the information specific to the recalled configuration file. An error message will be displayed if there is a conflict between current and recalled instrument addresses.

\*RST

This reset (RST) command resets most functions to factory-defined conditions. Each command shows \*RST value if the setting is affected.

\*SAV "<filename>"

The SAV command saves all applied configuration settings, channel settings, and external instrument information to the specified file name or path, for example, \*SAV ”C:\\ temp\\file.pxb ”

\*SRE <data>

The Service Request Enable (SRE) command sets the value of the Service Request Enable Register.

The variable <data> is the decimal sum of the bits that will be enabled. Bit 6 (value 64) is ignored and cannot be set by this command.

Range: 0–255

Entering values from 64 to 127 is equivalent to entering values from 0 to 63.

\*SRE?

The Service Request Enable (SRE) query returns the value of the Service Request Enable Register.

Range: 0–63 or 128–191

\*STB?

The Read Status Byte (STB) query returns the value of the status byte including the master summary status (MSS) bit without erasing its contents.

Range: 0–255

\*TRG

The Trigger command starts the waveform playing when the trigger source is set to Bus.

\* TST?

The Self-Test (TST) query initiates the internal self-test and returns one of the following results:

| 0 | This shows that all tests passed. |
| --- | --- |
| 1 | This shows that one or more tests failed. |

\* WAI

The Wait-to-Continue (WAI) command causes the instrument to wait until all pending commands are completed, before executing any other commands.
