import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { EmptyState } from '@/components/shared/EmptyState';
import { FileText } from 'lucide-react';

describe('EmptyState', () => {
  const defaultProps = {
    icon: FileText,
    title: 'No documents',
    description: 'Upload your first document to get started',
  };

  it('renders title and description', () => {
    render(<EmptyState {...defaultProps} />);
    expect(screen.getByText('No documents')).toBeInTheDocument();
    expect(screen.getByText('Upload your first document to get started')).toBeInTheDocument();
  });

  it('renders icon', () => {
    const { container } = render(<EmptyState {...defaultProps} />);
    const iconContainer = container.querySelector('.w-16.h-16');
    expect(iconContainer).toBeInTheDocument();
  });

  it('renders without action button by default', () => {
    render(<EmptyState {...defaultProps} />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const action = {
      label: 'Upload Document',
      onClick: vi.fn(),
    };
    render(<EmptyState {...defaultProps} action={action} />);
    expect(screen.getByRole('button', { name: 'Upload Document' })).toBeInTheDocument();
  });

  it('calls action onClick when button is clicked', () => {
    const onClick = vi.fn();
    const action = {
      label: 'Upload Document',
      onClick,
    };
    render(<EmptyState {...defaultProps} action={action} />);
    
    const button = screen.getByRole('button', { name: 'Upload Document' });
    fireEvent.click(button);
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('accepts custom className', () => {
    const { container } = render(<EmptyState {...defaultProps} className="custom-class" />);
    const wrapper = container.querySelector('.custom-class');
    expect(wrapper).toBeInTheDocument();
  });

  it('applies centered layout styles', () => {
    const { container } = render(<EmptyState {...defaultProps} />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center', 'text-center');
  });

  it('renders with different icon', () => {
    const { MessageSquare } = require('lucide-react');
    const { container } = render(
      <EmptyState
        icon={MessageSquare}
        title="No conversations"
        description="Start a new chat"
      />
    );
    expect(container.querySelector('.w-16.h-16')).toBeInTheDocument();
  });
});
