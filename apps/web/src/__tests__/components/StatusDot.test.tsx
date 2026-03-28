import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusDot } from '@/components/shared/StatusDot';

describe('StatusDot', () => {
  it('renders with default props', () => {
    const { container } = render(<StatusDot status="healthy" />);
    const dot = container.querySelector('span');
    expect(dot).toBeInTheDocument();
    expect(dot).toHaveClass('w-2', 'h-2', 'rounded-full');
  });

  it('renders with small size', () => {
    const { container } = render(<StatusDot status="healthy" size="sm" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('w-1.5', 'h-1.5');
  });

  it('renders with medium size', () => {
    const { container } = render(<StatusDot status="healthy" size="md" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('w-2', 'h-2');
  });

  it('applies correct color for healthy status', () => {
    const { container } = render(<StatusDot status="healthy" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-status-green');
  });

  it('applies correct color for error status', () => {
    const { container } = render(<StatusDot status="error" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-status-red');
  });

  it('applies correct color for warning status', () => {
    const { container } = render(<StatusDot status="warning" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-status-amber');
  });

  it('applies correct color for unknown status', () => {
    const { container } = render(<StatusDot status="unknown" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-text-muted');
  });

  it('maps ok status to healthy', () => {
    const { container } = render(<StatusDot status="ok" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-status-green');
  });

  it('maps pending status to warning', () => {
    const { container } = render(<StatusDot status="pending" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('bg-status-amber');
  });

  it('applies animation for healthy status', () => {
    const { container } = render(<StatusDot status="healthy" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('animate-pulse-dot');
  });

  it('applies animation for warning status', () => {
    const { container } = render(<StatusDot status="warning" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('animate-pulse-dot');
  });

  it('does not apply animation for error status', () => {
    const { container } = render(<StatusDot status="error" />);
    const dot = container.querySelector('span');
    expect(dot).not.toHaveClass('animate-pulse-dot');
  });

  it('accepts custom className', () => {
    const { container } = render(<StatusDot status="healthy" className="custom-class" />);
    const dot = container.querySelector('span');
    expect(dot).toHaveClass('custom-class');
  });
});
