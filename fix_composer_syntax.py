with open('frontend/src/components/Composer.tsx', 'r') as f:
    content = f.read()

content = content.replace('\\n  });\\n\\nComposer.displayName = "Composer";\\n', '\n  });\n\nComposer.displayName = "Composer";\n')

with open('frontend/src/components/Composer.tsx', 'w') as f:
    f.write(content)
