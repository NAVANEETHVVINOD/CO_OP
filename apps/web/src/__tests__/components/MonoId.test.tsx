import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MonoId } from '@/components/shared/MonoId';

describe('MonoId', () => {
  const mockId = 'abc123def456ghi789';

  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn(() => Promise.resolve()),
      },
    });
  });

  it('renders shortened ID by default', () => {
    render(<MonoId id={mockId} />);
    expect(screen.getByText('abc123de')).toBeInTheDocument();
  });

  it('renders custom number of characters', () => {
    render(<MonoId id={mockId} chars={4} />);
    expect(screen.getByText('abc1')).toBeInTheDocument();
  });

  it('displays full ID in title attribute', () => {
    const { container } = render(<MonoId id={mockId} />);
    const span = container.querySelector('span[title]');
    expect(span).toHaveAttribute('title', mockId);
  });

  it('shows copy button on hover', () => {
    render(<MonoId id={mockId} />);
    const button = screen.getByRole('button', { name: /copy full id/i });
    expect(button).toBeInTheDocument();
  });

  it('copies full ID to clipboard when clicked', async () => {
    render(<MonoId id={mockId} />);
    const button = screen.getByRole('button', { name: /copy full id/i });
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockId);
    });
  });

  it('shows check icon after copying', async () => {
    render(<MonoId id={mockId} />);
    const button = screen.getByRole('button', { name: /copy full id/i });
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(button.querySelector('svg')).toHaveClass('text-green');
    });
  });

  it('stops event propagation when copy button is clicked', async () => {
    const handleClick = vi.fn();
    const { container } = render(
      <div onClick={handleClick}>
        <MonoId id={mockId} />
      </div>
    );
    
    const button = screen.getByRole('button', { name: /copy full id/i });
    fireEvent.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('accepts custom className', () => {
    const { container } = render(<MonoId id={mockId} className="custom-class" />);
    const span = container.querySelector('.custom-class');
    expect(span).toBeInTheDocument();
  });

  it('renders ID in monospace font', () => {
    const { container } = render(<MonoId id={mockId} />);
    const idSpan = container.querySelector('.font-mono');
    expect(idSpan).toBeInTheDocument();
    expect(idSpan).toHaveTextContent('abc123de');
  });
});
