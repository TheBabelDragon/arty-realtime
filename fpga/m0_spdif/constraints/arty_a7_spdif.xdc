# Arty A7 — S/PDIF M0 pin constraints (PLACEHOLDER)
#
# Replace with actual PMOD / optical transceiver pins when hardware is chosen.
# Digilent Arty A7 reference: JA/JB/JC/JD PMODs.
#
# Example placeholders (DO NOT use until verified against schematic):

# set_property -dict { PACKAGE_PIN xx IOSTANDARD LVCMOS33 } [get_ports spdif_tx]
# set_property -dict { PACKAGE_PIN xx IOSTANDARD LVCMOS33 } [get_ports spdif_rx]
# set_property -dict { PACKAGE_PIN xx IOSTANDARD LVCMOS33 } [get_ports {led[0]}]; # LOCK
# set_property -dict { PACKAGE_PIN xx IOSTANDARD LVCMOS33 } [get_ports {led[1]}]; # MISMATCH

# Clock (Arty A7 100 MHz)
# set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports clk_100mhz]
# create_clock -add -name sys_clk -period 10.00 [get_ports clk_100mhz]
