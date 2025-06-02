from Device_Drivers.stellarnet_driverLibs import stellarnet_driver3 as sn


try:
    # Step 1: Install the USB driver for Python use
    print("\nInstalling the device driver")
    sn.installDeviceDriver()  # this is for initial setup for python
    

    print("\nOnce the driver install finishes, reconnect the spectrometer and rerun this test script.")

except Exception as e:
    print("\nFailed to install the driver.")
    print("Make sure you're running this script as Administrator!")
    print("Error message:", e)

