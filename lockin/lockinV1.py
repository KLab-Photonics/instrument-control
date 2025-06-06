import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from Device_Drivers import UHFLI, NewPort_Delay_Stage_225
import pandas as pd
import time


"""
README:

Requirements:

The pip packages required to run this script are in requirements.txt
~ you can pip install -r requirements.txt to install them.

This script uses two neccessary driver files: 
~ lockin_driver.py and move_stage_driver.py. The script in its own folder expects them to be in the Device_Drivers folder.

Main_Folder
│ 
├── Lockin_Script_Folder
│   ├── lockinV1.py
│ 
├── Device_Drivers_Folder
│   ├── lockin_driver.py
│   ├── move_stage_driver.py
│ 
├── requirements.txt

------------------------------------------------------------------------------------------------

This script performs the following steps:

1. Initializes the UHFLI Lock-In Amplifier and NewPort Delay Stage.
2. Collects Reference Transmission (T_ref) with no sample in.
3. Collects Normalized Transmission (NormT) with the sample in.
4. Collects Normalized Reflection (NormR).
5. Optionally performs a quick sweep to find the overlap peak (If the user wants).
6. Moves the stage to specified positions and collects data.
7. Calculates delay in picoseconds based on the stage position.
8. Exports the results to an Excel file on the Desktop.
9. Disconnects the devices after data collection.

"""

"""
For Tyler:

When running this script, look for errors within:
- Baseline turning on/off (check the driver file if this is wrong)
- The current delay outputs (check the main code for this) & find out why expected delay from files are not exactly at 0
    - also is it a two way optical or one way delay? (pos multiplied by 2 or not)
- The Quick Sweep functionality (only if the top two steps are done)
- Need to check the LabVIEW code for the quick sweep functionality in general.
"""

def main():
    # -------------------------------------------------------------------------------
    # Step 0: Initialize devices
    # The UHFLI class is the lock‑in amplifier, and NewPort_Delay_Stage_225 is the delay stage
    lockin = UHFLI()
    if not lockin.is_connected():
        print("Error: Didn't connect to the UHFLI")
        return
    stage = NewPort_Delay_Stage_225()
    if not stage.is_connected():
        print("Error: Didn't connect to the NewPort Delay Stage")
        lockin.disconnect()
        return
    # -------------------------------------------------------------------------------

    # Step 1: Reference Transmission (T_ref)
    input("Press Enter to collect 100% transmission (no sample in)... ")
    # Turn OFF boxcar‑1 baseline
    lockin.set_boxcar_baseline(1, 0)
    T_ref = lockin.average_boxcar_voltage(0)
    print(f"T_ref = {T_ref:.3f} mV")

    # Step 2: Normalized Transmission (NormT)
    input("Insert sample & press Enter to collect NormT... ")
    normT = lockin.average_boxcar_voltage(0)
    print(f"NormT = {normT:.3f} mV")
    # Turn ON boxcar‑1 baseline
    lockin.set_boxcar_baseline(1, 1)
 
    # Step 3: Normalized Reflection (NormR)
    input("Press Enter to collect NormR... ")
    # Turn OFF boxcar‑2 baseline
    lockin.set_boxcar_baseline(2, 0)
    normR = lockin.average_boxcar_voltage(1)
    print(f"NormR = {normR:.3f} mV")
    # Turn ON boxcar‑2 baseline
    lockin.set_boxcar_baseline(2, 1)
  
    # -------------------------------------------------------------------------------
    # Optional: Quick sweep to find overlap
    if input("Quick sweep to find overlap? (y/n): ").strip().lower() == 'y':
        start_pos = float(input("Enter stage START position in mm (e.g. 150.34): "))
        end_pos   = float(input("Enter stage END position in mm (e.g. 160.67): "))
        ss = float(input("Enter each step size in mm: "))
        sweep_positions = stage.quick_sweep(start_pos, end_pos, ss)

        max_voltage = float('-inf')
        max_pos = None

        for pos in sweep_positions:
            voltage = lockin.read_boxcar_voltage(0)
            print(f"Pos: {pos:.3f} mm, Voltage: {voltage:.3f} mV")
            if voltage > max_voltage:
                max_voltage = voltage
                max_pos = pos

        print(f"\nQuick sweep done >>> Overlap peak voltage found at {max_pos:.3f} mm: {max_voltage:.3f} mV")
        stage.close()
        lockin.disconnect()
        print("Devices disconnected, exiting program.")
        return
    # -------------------------------------------------------------------------------

    # Step 4: Movement setup
    while True:
        start_pos = float(input("Enter stage START position in mm (e.g. 150.345): "))
        end_pos   = float(input("Enter stage END position in mm (e.g. 160.675): "))
        confirm = input(f"Start and End Positions Correct (y/n)?\n"f">>> START: {start_pos} >>> END: {end_pos}\n").strip().lower()
        if confirm == 'y':
            break

    steps = int(input("Enter number of steps: "))
    if steps < 2:
        print("Number of steps should be at least 2")
        return
    step_size = (end_pos - start_pos) / (steps - 1)
    positions = [round(start_pos + i * step_size, 2) for i in range(steps)]

    print(f"Step size: {step_size:.3f} mm")
    print(f"Positions: {positions}")

    
    # Setup storage arrays
    dT, dR, dA = [], [], []
    dT_p, dR_p, dA_p = [], [], []
    delays_ps = []
    recorded_positions = []
   
    
    # Step 5: Data collection & math
    try:    #try here to ensure devices are closed properly even if an error occurs
        
        print("Starting data collection...")
        for i, pos in enumerate(positions):
            print(f"\nStep {i}/{steps}: Moving to {pos} mm")
            stage.move_to(pos)
            time.sleep(0.4)  # 400 ms delay for stage to settle

            # Read raw voltages from boxcars
            dt = lockin.read_boxcar_voltage(0)
            dr = lockin.read_boxcar_voltage(1)

            # Calculations (verify these formulas)
            da = - (dt + dr)
            t_prct = (dt / T_ref) * 100
            r_prct = (dr / T_ref) * 100
            a_prct = (da / T_ref) * 100
            rel_pos = pos - start_pos
            delay_ps = (2 * rel_pos / 1000) / 3e8 * 1e12 # Convert mm to m, then to seconds, then to picoseconds (Should be multiplied by 2)

            # Append results to storage arrays
            dT.append(dt)
            dR.append(dr)
            dA.append(da)
            recorded_positions.append(pos)
            dT_p.append(t_prct)
            dR_p.append(r_prct)
            dA_p.append(a_prct)
            delays_ps.append(delay_ps)

            # Print results for each data collection step (Can remove if desired, for debugging)
            print(f"Step {i}/{steps}:")
            print(f"  Position: {pos} mm, Delay: {delay_ps:.2f} ps")
            print(f"  dT = {dt:.3f} mV, dR = {dr:.3f} mV, dA = {da:.3f} mV")
            print(f"  %T = {t_prct:.2f}, %R = {r_prct:.2f}, %A = {a_prct:.2f}")
    
    
    # Step 6: Disconnect devices
    finally:    #make sure devices are closed properly
        try:
            stage.close()
        except Exception:   
            pass
        try:
            lockin.disconnect()
        except Exception:
            pass
        print("Devices disconnected.")
    
    
    # Step 7: Peak detection & delay repositioning for excel 
    peak_index = dT.index(max(dT, key = abs))
    peak_position = positions[peak_index]
    delays_ps = [((pos - peak_position) * 2 / 1000) / 3e8 * 1e12 for pos in positions] # Convert mm to m, then to seconds, then to picoseconds


    # Step 8: Exporting results to Excel
    desktop_path = Path.home() / "Desktop" / "RTA_readings.xlsx"
    writer = pd.ExcelWriter(desktop_path, engine='xlsxwriter')

    # Summary row with T_ref, NormT, NormR
    pd.DataFrame([[T_ref, normT, normR]],columns=["Absolute Transmission", "NormT", "NormR"]).to_excel(writer, index=False, startrow=0, startcol=0)

    # Full table of measured data
    pd.DataFrame({
        "Position [mm]": recorded_positions,
        "Delay [ps]": delays_ps,
        "dT [mV]": dT,
        "dR [mV]": dR,
        "dA [mV]": dA,
        "dT [%]": dT_p,
        "dR [%]": dR_p,
        "dA [%]": dA_p
    }).to_excel(writer, index=False, startrow=0, startcol=4)

    writer.close()
    print(f"Results saved to {desktop_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped.")

