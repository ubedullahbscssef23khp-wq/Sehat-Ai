with open("frontend/src/components/ClinicianSummaryView.tsx", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('  return lines.join("'):
        new_lines.append('  return lines.join("\\n");\n')
    elif line.strip() == '");}':
        pass
    else:
        new_lines.append(line)

with open("frontend/src/components/ClinicianSummaryView.tsx", "w") as f:
    f.writelines(new_lines)
