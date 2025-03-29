import base64
import struct
import argparse
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

class FirmwareBinaryAnalyzer:
    def __init__(self, binary_data=None, file_path=None):
        """Initialize with either binary data directly or a file path"""
        if binary_data:
            self.data = binary_data
        elif file_path:
            with open(file_path, 'rb') as f:
                self.data = f.read()
        else:
            raise ValueError("Either binary_data or file_path must be provided")
        
        self.size = len(self.data)
        self.summary = {}
    
    @classmethod
    def from_base64(cls, base64_string):
        """Create an analyzer from a base64 encoded string"""
        binary_data = base64.b64decode(base64_string)
        return cls(binary_data=binary_data)
    
    def get_basic_info(self):
        """Get basic information about the binary file"""
        self.summary = {
            "file_size": self.size,
            "null_bytes_percentage": self.count_null_bytes() / self.size * 100 if self.size > 0 else 0,
            "entropy": self.calculate_entropy(),
            "potential_type": self.guess_file_type(),
            "text_strings": len(self.extract_strings()),
        }
        return self.summary
    
    def count_null_bytes(self):
        """Count the number of null bytes in the binary data"""
        return self.data.count(b'\x00')
    
    def calculate_entropy(self):
        """Calculate Shannon entropy of the binary data"""
        if not self.data:
            return 0
        
        byte_counts = {}
        for byte in self.data:
            if byte in byte_counts:
                byte_counts[byte] += 1
            else:
                byte_counts[byte] = 1
        
        entropy = 0
        for count in byte_counts.values():
            probability = count / self.size
            entropy -= probability * np.log2(probability)
        
        return entropy
    
    def guess_file_type(self):
        """Attempt to guess the file type based on patterns"""
        if self.size < 4:
            return "Unknown (too small)"
        
        # Check for common headers
        if self.data.startswith(b'\x7FELF'):
            return "ELF executable"
        elif self.data.startswith(b'MZ'):
            return "Windows PE executable"
        elif self.data.startswith(b'\xFF\xD8\xFF'):
            return "JPEG image"
        elif self.data.startswith(b'\x89PNG'):
            return "PNG image"
        
        # Look for patterns that suggest firmware
        null_percentage = self.count_null_bytes() / self.size * 100
        if null_percentage > 50 and self.size > 1024:
            return "Possible firmware (high null byte count)"
        
        # Check for ARM code patterns (common in embedded firmware)
        # Simple heuristic - look for common ARM instruction patterns
        if self.size > 32:
            arm_patterns = [b'\x10\xB5', b'\x00\xBD', b'\xF0\xB5', b'\xF0\xBD']  # Some common Thumb instruction patterns
            for pattern in arm_patterns:
                if pattern in self.data:
                    return "Possible ARM firmware"
        
        return "Unknown binary format"
    
    def extract_strings(self, min_length=4):
        """Extract ASCII strings from the binary data"""
        strings = []
        current_string = ""
        
        for byte in self.data:
            # If it's a printable ASCII character
            if 32 <= byte <= 126:
                current_string += chr(byte)
            else:
                # End of a string
                if len(current_string) >= min_length:
                    strings.append(current_string)
                current_string = ""
        
        # Check for the last string
        if len(current_string) >= min_length:
            strings.append(current_string)
            
        return strings
    
    def visualize_data(self):
        """Create a visualization of the binary data as a heatmap"""
        # Calculate a suitable width for the array
        width = min(16, self.size)
        if width == 0:
            return None
            
        height = self.size // width + (1 if self.size % width else 0)
        
        # Create a 2D array from the binary data
        data_array = np.zeros((height, width), dtype=np.uint8)
        for i in range(self.size):
            row = i // width
            col = i % width
            if row < height and col < width:
                data_array[row, col] = self.data[i]
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(data_array, cmap='viridis', aspect='auto')
        plt.colorbar(label='Byte value')
        plt.title('Binary Data Visualization')
        plt.xlabel('Byte offset (mod width)')
        plt.ylabel('Row')
        
        # Convert plot to image data in memory
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def find_patterns(self, pattern_size=4):
        """Find repeating patterns in the binary data"""
        if self.size < pattern_size * 2:
            return []
            
        patterns = {}
        for i in range(self.size - pattern_size + 1):
            pattern = self.data[i:i+pattern_size]
            if pattern in patterns:
                patterns[pattern].append(i)
            else:
                patterns[pattern] = [i]
        
        # Filter out patterns that don't repeat
        repeating_patterns = {k: v for k, v in patterns.items() if len(v) > 1}
        
        # Sort by frequency
        sorted_patterns = sorted(repeating_patterns.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Return top patterns
        return sorted_patterns[:10] if sorted_patterns else []
    
    def search_for_headers(self):
        """Search for known firmware headers or markers"""
        common_headers = {
            b'\x7FELF': "ELF header",
            b'MZ': "DOS/PE header",
            b'\xEB\x3C\x90': "x86 boot sector",
            b'\x55\xAA': "x86 boot signature (at end of sector)",
            b'\xAA\x55': "x86 boot signature (little endian)",
            b'\x23\x20\x44\x65': "Shell script (# De)",
            b'\x23\x21\x2F\x62\x69\x6E': "Unix script (#!/bin)",
            b'\x23\x21\x2F\x75\x73\x72': "Unix script (#!/usr)",
        }
        
        found_headers = {}
        for header, description in common_headers.items():
            positions = []
            pos = 0
            while True:
                pos = self.data.find(header, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
            
            if positions:
                found_headers[description] = positions
        
        return found_headers
    
    def analyze_structure(self, chunk_size=16):
        """Analyze the structure by breaking the binary into chunks and summarizing"""
        if not self.data or self.size < chunk_size:
            return []
        
        chunks = []
        for i in range(0, self.size, chunk_size):
            chunk = self.data[i:i+chunk_size]
            null_percentage = chunk.count(b'\x00') / len(chunk) * 100
            non_ascii = sum(1 for b in chunk if b < 32 or b > 126) / len(chunk) * 100
            
            chunk_type = "Unknown"
            if null_percentage > 90:
                chunk_type = "Empty/Padding"
            elif null_percentage < 10 and non_ascii < 10:
                chunk_type = "Possible Text"
            elif null_percentage < 50 and non_ascii > 80:
                chunk_type = "Possible Code or Data"
            
            chunks.append({
                "offset": i,
                "size": len(chunk),
                "null_percentage": null_percentage,
                "non_ascii_percentage": non_ascii,
                "type": chunk_type,
                "first_bytes": chunk[:4].hex()
            })
        
        return chunks
    
    def export_to_file(self, file_path):
        """Export the binary data to a file"""
        with open(file_path, 'wb') as f:
            f.write(self.data)
        return file_path
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        self.get_basic_info()
        
        report = []
        report.append("# Firmware Binary Analysis Report")
        report.append("")
        
        # Basic info
        report.append("## Basic Information")
        report.append(f"- File Size: {self.summary['file_size']} bytes")
        report.append(f"- Null Bytes: {self.summary['null_bytes_percentage']:.2f}%")
        report.append(f"- Entropy: {self.summary['entropy']:.4f}")
        report.append(f"- Potential File Type: {self.summary['potential_type']}")
        report.append(f"- Text Strings Count: {self.summary['text_strings']}")
        report.append("")
        
        # Headers
        headers = self.search_for_headers()
        if headers:
            report.append("## Found Headers")
            for header, positions in headers.items():
                pos_str = ", ".join([f"0x{pos:X}" for pos in positions[:5]])
                if len(positions) > 5:
                    pos_str += f", ... ({len(positions) - 5} more)"
                report.append(f"- {header}: at offsets {pos_str}")
            report.append("")
        
        # Strings
        strings = self.extract_strings(min_length=6)  # Longer strings for report
        if strings:
            report.append("## Text Strings")
            for i, string in enumerate(strings[:20]):  # Limit to 20 strings
                report.append(f"- \"{string}\"")
            if len(strings) > 20:
                report.append(f"- ... ({len(strings) - 20} more strings)")
            report.append("")
        
        # Structure analysis
        report.append("## Structure Analysis")
        chunks = self.analyze_structure(chunk_size=32)  # Larger chunks for the report
        
        # Group similar chunks
        current_type = None
        chunk_group = []
        for i, chunk in enumerate(chunks):
            if chunk["type"] != current_type:
                if chunk_group:
                    start = chunk_group[0]["offset"]
                    end = chunk_group[-1]["offset"] + chunk_group[-1]["size"]
                    report.append(f"- {current_type} region: 0x{start:X} - 0x{end:X} ({end - start} bytes)")
                
                current_type = chunk["type"]
                chunk_group = [chunk]
            else:
                chunk_group.append(chunk)
                
            # Process last group
            if i == len(chunks) - 1 and chunk_group:
                start = chunk_group[0]["offset"]
                end = chunk_group[-1]["offset"] + chunk_group[-1]["size"]
                report.append(f"- {current_type} region: 0x{start:X} - 0x{end:X} ({end - start} bytes)")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Analyze firmware binary files")
    parser.add_argument("--file", help="Path to the binary file")
    parser.add_argument("--base64", help="Base64 encoded binary data")
    parser.add_argument("--output", help="Output file for the report")
    parser.add_argument("--extract", help="Extract the binary to a file")
    parser.add_argument("--visualize", help="Save visualization to a file")
    
    args = parser.parse_args()
    
    if not args.file and not args.base64:
        print("Error: Either --file or --base64 must be provided")
        parser.print_help()
        return
    
    # Create analyzer
    if args.file:
        analyzer = FirmwareBinaryAnalyzer(file_path=args.file)
    else:
        analyzer = FirmwareBinaryAnalyzer.from_base64(args.base64)
    
    # Generate and print report
    report = analyzer.generate_report()
    print(report)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    
    # Extract binary if requested
    if args.extract:
        analyzer.export_to_file(args.extract)
        print(f"Binary data extracted to {args.extract}")
    
    # Visualize if requested
    if args.visualize:
        vis_buf = analyzer.visualize_data()
        if vis_buf:
            with open(args.visualize, 'wb') as f:
                f.write(vis_buf.getvalue())
            print(f"Visualization saved to {args.visualize}")
        else:
            print("Could not create visualization (empty data)")


if __name__ == "__main__":
    main()
