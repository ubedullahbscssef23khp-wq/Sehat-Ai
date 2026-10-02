import re

with open("frontend/src/components/ClinicianSummaryView.tsx", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("  return lines.join("):
        new_lines.append('  return lines.join("\\n");\n')
    elif line.startswith('}'):
        if len(new_lines) > 0 and new_lines[-1].startswith('  return lines.join('):
            new_lines.append('}\n')
        elif len(new_lines) > 0 and new_lines[-1].strip() == '":':
            # pop bad lines
            new_lines.pop()
            if new_lines[-1].startswith('  return lines.join('):
                new_lines.pop()
            new_lines.append('  return lines.join("\\n");\n}\n')
        else:
            new_lines.append(line)
    elif line.strip() == '":':
        pass
    else:
        new_lines.append(line)

with open("frontend/src/components/ClinicianSummaryView.tsx", "w") as f:
    f.writelines(new_lines)

