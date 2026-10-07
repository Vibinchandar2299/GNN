from typing import Dict, Any, List, Optional
from ai_service.app.services.inference_service import inference_service
from ai_service.app.core.logging import logger

class GraphService:
    """
    Service for querying graph topology and neighborhood subgraphs for visualization.
    """
    def __init__(self):
        pass

    def get_node_neighborhood(
        self,
        node_type: str,
        entity_id: str,
        max_neighbors: int = 50
    ) -> Dict[str, Any]:
        """
        Retrieves the 1-hop subgraph neighborhood for a given entity:
        - node_type: 'application', 'student', 'company', 'job', 'skill'
        - entity_id: e.g. 'A00010', 'S1654', 'C014', 'J0263', 'SK_13'
        """
        if not inference_service.is_initialized:
            raise RuntimeError("InferenceService is not initialized.")

        clean_type = node_type.lower().strip()
        clean_id = str(entity_id).strip()

        if clean_type not in inference_service.node_maps:
            valid_types = list(inference_service.node_maps.keys())
            raise ValueError(f"Invalid node_type '{clean_type}'. Valid types: {valid_types}")

        type_map = inference_service.node_maps[clean_type]
        if clean_id not in type_map:
            raise KeyError(f"Entity '{clean_id}' of type '{clean_type}' not found in graph.")

        center_idx = type_map[clean_id]
        edge_index = inference_service.graph_data.edge_index
        edge_type = inference_service.graph_data.edge_type

        # Find incoming and outgoing edges
        src_tensor = edge_index[0]
        dst_tensor = edge_index[1]

        # Edges originating from center
        out_mask = (src_tensor == center_idx)
        # Edges pointing to center
        in_mask = (dst_tensor == center_idx)

        connected_edges_mask = out_mask | in_mask
        edge_indices = connected_edges_mask.nonzero(as_tuple=True)[0]

        if len(edge_indices) > max_neighbors:
            edge_indices = edge_indices[:max_neighbors]

        neighbor_node_ids = set()
        neighbor_node_ids.add(center_idx)

        links = []
        for e_idx in edge_indices:
            s_idx = int(src_tensor[e_idx].item())
            d_idx = int(dst_tensor[e_idx].item())
            r_id = int(edge_type[e_idx].item())
            r_name = inference_service.id_to_relation.get(r_id, f"REL_{r_id}")

            neighbor_node_ids.add(s_idx)
            neighbor_node_ids.add(d_idx)

            s_type, s_eid = inference_service.node_id_to_entity.get(s_idx, ("unknown", str(s_idx)))
            d_type, d_eid = inference_service.node_id_to_entity.get(d_idx, ("unknown", str(d_idx)))

            links.append({
                "source": s_eid,
                "source_type": s_type,
                "target": d_eid,
                "target_type": d_type,
                "relation": r_name,
                "relation_id": r_id
            })

        nodes = []
        for n_idx in neighbor_node_ids:
            n_type, n_eid = inference_service.node_id_to_entity.get(n_idx, ("unknown", str(n_idx)))
            nodes.append({
                "id": n_eid,
                "node_index": n_idx,
                "type": n_type,
                "is_center": (n_idx == center_idx)
            })

        return {
            "center_node": {
                "id": clean_id,
                "type": clean_type,
                "node_index": center_idx
            },
            "nodes_count": len(nodes),
            "links_count": len(links),
            "nodes": nodes,
            "links": links
        }

graph_service = GraphService()
