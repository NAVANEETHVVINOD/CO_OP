'use client';

import { useState, useEffect } from 'react';
import { Briefcase, Calendar, CheckCircle2, Clock, Check, Loader2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { toast } from 'sonner';

interface Milestone {
  id: string;
  title: string;
  status: string;
  due_date?: string;
}

interface Project {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  milestones?: Milestone[];
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [completingId, setCompletingId] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      const res = await apiFetch('/v1/projects');
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      }
    } catch {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCompleteMilestone = async (milestoneId: string) => {
    setCompletingId(milestoneId);
    try {
      const res = await apiFetch(`/v1/projects/milestones/${milestoneId}/complete`, {
        method: 'POST'
      });
      if (res.ok) {
        toast.success('Milestone completed');
        fetchProjects(); // Refresh list
      } else {
        toast.error('Failed to complete milestone');
      }
    } catch {
      toast.error('An error occurred');
    } finally {
      setCompletingId(null);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 text-primary">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Projects</h1>
        <p className="text-secondary">Monitor active engagements and milestones.</p>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <Loader2 className="animate-spin h-8 w-8 text-accent" />
        </div>
      ) : projects.length === 0 ? (
        <div className="border border-dim rounded-xl p-12 text-center bg-surface">
          <Briefcase className="mx-auto h-12 w-12 text-muted mb-4 opacity-20" />
          <h3 className="text-lg font-medium">No active projects</h3>
          <p className="text-secondary mt-2">Projects will appear here once proposals are accepted.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-8">
          {projects.map((project) => (
            <div key={project.id} className="border border-dim rounded-xl bg-surface overflow-hidden">
              <div className="p-6 border-b border-dim bg-elevated/30 flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="p-2.5 rounded-lg bg-accent/10 text-accent">
                    <Briefcase size={24} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-primary">{project.title}</h2>
                    <div className="flex items-center gap-2 text-[11px] text-muted font-medium mt-1">
                      <Calendar size={12} />
                      <span className="uppercase tracking-widest">Started {new Date(project.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-widest px-3 py-1.5 rounded-full ${
                  project.status === 'active' ? 'bg-green-status/10 text-green-status border border-green-status/20' : 'bg-muted/10 text-muted border border-muted/20'
                }`}>
                  {project.status}
                </span>
              </div>
              
              <div className="p-6 space-y-6">
                <div className="max-w-3xl">
                  <h3 className="text-[12px] font-bold text-muted uppercase tracking-wider mb-2">Description</h3>
                  <p className="text-secondary text-sm leading-relaxed">{project.description}</p>
                </div>

                <div className="space-y-4">
                  <h3 className="text-[12px] font-bold text-muted uppercase tracking-wider">Milestones</h3>
                  <div className="grid grid-cols-1 gap-3">
                    {project.milestones && project.milestones.length > 0 ? (
                      project.milestones.map((m: Milestone) => (
                        <div key={m.id} className="flex items-center justify-between p-4 rounded-lg bg-elevated/50 border border-dim group hover:border-dim-highlight transition-colors">
                          <div className="flex items-center gap-4">
                            <div className={`p-1.5 rounded-full ${m.status === 'completed' ? 'bg-green-status/20 text-green-status' : 'bg-muted/20 text-muted'}`}>
                              {m.status === 'completed' ? <CheckCircle2 size={16} /> : <Clock size={16} />}
                            </div>
                            <div>
                              <p className={`text-sm font-semibold ${m.status === 'completed' ? 'text-muted line-through' : 'text-primary'}`}>
                                {m.title}
                              </p>
                              {m.due_date && (
                                <p className="text-[11px] text-muted mt-0.5">
                                  Due {new Date(m.due_date).toLocaleDateString()}
                                </p>
                              )}
                            </div>
                          </div>
                          
                          {m.status !== 'completed' && (
                            <button
                              onClick={() => handleCompleteMilestone(m.id)}
                              disabled={completingId === m.id}
                              className="opacity-0 group-hover:opacity-100 flex items-center gap-2 px-3 py-1.5 rounded-md bg-accent/10 text-accent text-[11px] font-bold uppercase tracking-wider hover:bg-accent hover:text-white transition-all disabled:opacity-50"
                            >
                              {completingId === m.id ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
                              Complete
                            </button>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-muted italic">No milestones defined for this project.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
