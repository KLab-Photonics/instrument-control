import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from Device_Drivers import stellarnet_driver3 as sn
from Device_Drivers import NewPort_Delay_Stage_225  
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# inputs for Spectrometer
def main():
    try:
        integration_time = int(input("Enter integration time (ms): "))
        scans_avg = int(input("Enter number of scans to average: "))
        Digitizer_CRS = int(input("Enter digitizer clock rate (e.g., 3): "))
        smooth = int(input("Enter optical smoothing level (0 = none): "))
        spec_channel = int(input("Enter spectral channel (0/1 = default): "))

        # Inputs for Stage
        start_pos = float(input("Enter stage START position (mm): "))
        stop_pos = float(input("Enter stage STOP position (mm): "))
        num_steps = int(input("Enter number of steps (integer): "))

        if num_steps < 2:
            raise ValueError("Number of steps must be at least 2.")
    
    except ValueError as ve:
        print("Invalid input:", ve)
        sys.exit()

    # Calculate Stage Positions
    step_size = (stop_pos - start_pos) / (num_steps - 1)
    positions = [round(start_pos + i * step_size, 3) for i in range(num_steps)]

    # Convert Positions to Delay Times (in ps)
    # Correct (one‐way mechanical to time in ps):
    delay_times_ps = [round((2*pos/1000)  / 3e8 * 1e12, 5) for pos in positions] # Multiply pos by 2 for two way if this is the case

    print(f"Stage positions: {positions}")

    # Setup Devices
    print("\nDriver Version:", sn.version())
    try:
        spec, wav = sn.array_get_spec(spec_channel)
        device_id = sn.getDeviceId(spec)
        if not sn.deviceConnectionCheck(spec):
            raise Exception("Device not connected.")
        print("Connected to Spectrometer:", device_id)

        # Set spectrometer parameters
        sn.setParam(spec, integration_time, scans_avg, smooth, Digitizer_CRS, clear=True)

        # delay stage
        stage = NewPort_Delay_Stage_225()
        print(f"Stage initialized on port {stage.ser.port}. Beginning scan")

        spectra = []
        actual_positions = []
        
        try:
            for i, pos in enumerate(positions):
                print(f"\nMoving to {pos} mm ({i+1}/{len(positions)})")
                stage.move_to(pos)

                print("Taking data readings")
                spectrum = sn.array_spectrum(spec, wav)
                spectra.append(spectrum)
                actual_positions.append(pos)
        finally:
            #close devices
            sn.reset(spec)
            stage.close()
            print(" >>> Scan complete.")

        #plotting data on 2D and 3D plots
        spectra_array = np.array(spectra)  # shape: (num_steps, num_wavelengths)
        fig = plt.figure(figsize=(14, 6))

        # 2D plot (left side)
        ax1 = fig.add_subplot(1, 2, 1)
        spectrum_idx = 0  # Change to another index to plot a different spectrum
        ax1.plot(wav, spectra_array[spectrum_idx, :])
        ax1.set_title(f"2D: Spectrum at Step {spectrum_idx+1}")
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("Amplitude (a.u.)")
        ax1.grid(True)

        # 3D subplot (right side)
        ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        X, Y = np.meshgrid(delay_times_ps, wav) 
        Z = spectra_array.T

        surf = ax2.plot_surface(X, Y, Z, cmap='plasma', linewidth=0, antialiased=False)
        ax2.set_title("3D Surface: Time vs Wavelength vs Counts")
        ax2.set_xlabel("Time (ps)")
        ax2.set_ylabel("Wavelength (nm)")
        ax2.set_zlabel("Counts")

        fig.colorbar(surf, ax=ax2, shrink=0.5, aspect=10, label="Counts")

        plt.tight_layout()
        plt.show()

        #Save to excel
        desktop_path = Path.home() / "Desktop" / "Spectrometer_readings.xlsx"

        data_rows = []
        for i, spectrum in enumerate(spectra):
            row = [actual_positions[i], delay_times_ps[i]] + list(spectrum)
            data_rows.append(row)

        column_headers = ["Stage Position (mm)", "Delay Time (ps)"] + [f"{w:.2f} nm" for w in wav]
        df = pd.DataFrame(data_rows, columns=column_headers)

        with pd.ExcelWriter(desktop_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Spectra Data')

        print("Data saved to Spectrometer_readings.xlsx on your Desktop.")

    except Exception as e:
        print("Error during run:")
        print("Error:", e)
        sys.exit()
    
    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            print("\nProgram stopped.")

