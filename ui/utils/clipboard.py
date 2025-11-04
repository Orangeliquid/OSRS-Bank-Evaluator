import pyperclip


def verify_tsv():
    clipboard_text = pyperclip.paste()

    if "\t" not in clipboard_text or "\n" not in clipboard_text:
        return False

    lines = [line for line in clipboard_text.splitlines() if line.strip()]
    if not lines or len(lines) < 2:
        return False

    split_counts = [len(line.split("\t")) for line in lines]
    avg_cols = sum(split_counts) / len(split_counts)
    consistent = all(abs(c - avg_cols) < 1 for c in split_counts)

    return consistent, clipboard_text


if verify_tsv():
    print("✅ Clipboard appears to contain valid TSV data.")
else:
    print("❌ Clipboard does not appear to contain valid TSV data.")

