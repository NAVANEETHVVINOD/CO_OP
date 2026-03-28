import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PageHeader } from '@/components/shared/PageHeader';

describe('PageHeader', () => {
  it('renders title', () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<PageHeader title="Dashboard" description="System overview" />);
    expect(screen.getByText('System overview')).toBeInTheDocument();
  });

  it('does not render description when not provided', () => {
    const { container } = render(<PageHeader title="Dashboard" />);
    const description = container.querySelector('p');
    expect(description).not.toBeInTheDocument();
  });

  it('renders badge when provided as number', () => {
    render(<PageHeader title="Documents" badge={42} />);
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders badge when provided as string', () => {
    render(<PageHeader title="Documents" badge="5 active" />);
    expect(screen.getByText('5 active')).toBeInTheDocument();
  });

  it('does not render badge when not provided', () => {
    const { container } = render(<PageHeader title="Dashboard" />);
    const badge = container.querySelector('.font-mono');
    expect(badge).not.toBeInTheDocument();
  });

  it('renders badge with value 0', () => {
    render(<PageHeader title="Documents" badge={0} />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders actions when provided', () => {
    const actions = <button>Upload</button>;
    render(<PageHeader title="Documents" actions={actions} />);
    expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
  });

  it('does not render actions section when not provided', () => {
    const { container } = render(<PageHeader title="Dashboard" />);
    const actionsDiv = container.querySelector('.flex.items-center.gap-3');
    // Should only have the title section, not actions
    expect(container.querySelectorAll('.flex.items-center.gap-3')).toHaveLength(1);
  });

  it('accepts custom className', () => {
    const { container } = render(<PageHeader title="Dashboard" className="custom-class" />);
    const header = container.querySelector('.custom-class');
    expect(header).toBeInTheDocument();
  });

  it('applies border bottom styling', () => {
    const { container } = render(<PageHeader title="Dashboard" />);
    const header = container.firstChild as HTMLElement;
    expect(header).toHaveClass('border-b', 'border-dim');
  });

  it('renders all props together', () => {
    const actions = <button>Action</button>;
    render(
      <PageHeader
        title="Documents"
        description="Manage your files"
        badge={10}
        actions={actions}
        className="custom"
      />
    );
    
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Manage your files')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });
});
