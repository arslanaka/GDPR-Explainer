'use client';

import React from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { ArticleDetail } from '@/lib/api';

interface GraphVizProps {
    data: ArticleDetail;
}

export default function GraphViz({ data }: GraphVizProps) {
    const elements = React.useMemo(() => {
        const nodes: any[] = [];
        const edges: any[] = [];

        // 1. Central Article Node
        nodes.push({
            data: { id: data.id, label: `Art. ${data.number}`, type: 'article' },
            position: { x: 0, y: 0 },
        });

        // 2. Obligations & Roles
        data.obligations.forEach((obl, idx) => {
            const oblId = `obl-${idx}`;
            nodes.push({
                data: { id: oblId, label: 'Obligation', type: 'obligation', tooltip: obl.summary },
            });
            edges.push({
                data: { source: data.id, target: oblId, label: 'HAS_OBLIGATION' },
            });

            // Role
            const roleId = `role-${obl.role.replace(/\s+/g, '-')}`;
            if (!nodes.find((n) => n.data.id === roleId)) {
                nodes.push({
                    data: { id: roleId, label: obl.role, type: 'role' },
                });
            }
            edges.push({
                data: { source: oblId, target: roleId, label: 'APPLIES_TO' },
            });
        });

        // 3. Terms
        data.terms.forEach((term, idx) => {
            const termId = `term-${idx}`;
            nodes.push({
                data: { id: termId, label: term.term, type: 'term', tooltip: term.definition },
            });
            edges.push({
                data: { source: data.id, target: termId, label: 'DEFINES' },
            });
        });

        // 4. Related Articles
        data.references.forEach((ref) => {
            const refId = ref.id;
            nodes.push({
                data: { id: refId, label: `Art. ${ref.number}`, type: 'article' },
            });
            edges.push({
                data: { source: data.id, target: refId, label: 'REFERS_TO' },
            });
        });

        return [...nodes, ...edges];
    }, [data]);

    const layout = {
        name: 'cose',
        animate: false,
        nodeDimensionsIncludeLabels: true,
        padding: 50,
    };

    const stylesheet: cytoscape.Stylesheet[] = [
        {
            selector: 'node',
            style: {
                'background-color': '#666',
                label: 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#fff',
                'text-outline-width': 2,
                'text-outline-color': '#666',
                width: 60,
                height: 60,
            },
        },
        {
            selector: 'node[type="article"]',
            style: {
                'background-color': '#2563eb', // Blue
                'text-outline-color': '#2563eb',
                width: 80,
                height: 80,
                'font-size': 14,
            },
        },
        {
            selector: 'node[type="obligation"]',
            style: {
                'background-color': '#dc2626', // Red
                'text-outline-color': '#dc2626',
                width: 40,
                height: 40,
                'font-size': 10,
            },
        },
        {
            selector: 'node[type="role"]',
            style: {
                'background-color': '#16a34a', // Green
                'text-outline-color': '#16a34a',
                shape: 'diamond',
            },
        },
        {
            selector: 'node[type="term"]',
            style: {
                'background-color': '#9333ea', // Purple
                'text-outline-color': '#9333ea',
                shape: 'triangle',
            },
        },
        {
            selector: 'edge',
            style: {
                width: 2,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                label: 'data(label)',
                'font-size': 8,
                'text-rotation': 'autorotate',
                'text-background-color': '#fff',
                'text-background-opacity': 1,
            },
        },
    ];

    return (
        <div className="h-[500px] w-full border rounded-xl bg-slate-50 overflow-hidden">
            <CytoscapeComponent
                elements={elements}
                style={{ width: '100%', height: '100%' }}
                layout={layout}
                stylesheet={stylesheet}
                cy={(cy) => {
                    cy.on('tap', 'node', (evt) => {
                        const node = evt.target;
                        console.log('tapped ' + node.id());
                        // Could show tooltip here
                    });
                }}
            />
        </div>
    );
}
