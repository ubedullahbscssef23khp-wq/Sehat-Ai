import re

with open("frontend/src/__tests__/Composer.test.tsx", "r") as f:
    content = f.read()

# Mock Speech Recognition at the top of the test file
mock_setup = """import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { Composer } from "../components/Composer";
import { strings } from "../i18n/strings";

describe("Composer", () => {
  beforeEach(() => {
    (window as any).SpeechRecognition = vi.fn();
  });
  afterEach(() => {
    delete (window as any).SpeechRecognition;
  });
"""

content = re.sub(
    r'import \{ render, screen \} from "@testing-library/react";.*?describe\("Composer", \(\) => \{',
    mock_setup,
    content,
    flags=re.DOTALL
)

with open("frontend/src/__tests__/Composer.test.tsx", "w") as f:
    f.write(content)
