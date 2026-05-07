import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CopyButton } from "./CopyButton";

describe("CopyButton", () => {
  it("writes the value to the clipboard and shows a confirmation", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<CopyButton value="https://x.test/abc" />);
    fireEvent.click(screen.getByRole("button", { name: /copy https:\/\/x\.test\/abc/i }));

    await waitFor(() => expect(writeText).toHaveBeenCalledWith("https://x.test/abc"));
    expect(await screen.findByText(/copied/i)).toBeInTheDocument();
  });
});
