import { Network } from "vis-network";
import { DataSet, DataView } from 'vis-data';
import React, { useEffect, useState, useRef } from "react";
import axiosGraphInfo from "./axios";


const MainGraph = () => {
  const [nodes, setNodes] = useState<any>([]);
  const [edges, setEdges] = useState<any>([]);
  const [network, setNetwork] = useState<Network>();

  const [tagforfilter, setTagforfilter] = useState<string>("");
  const container = useRef<HTMLDivElement>(null);

  const nodeFilter = (node: any) => {
    if (tagforfilter === "") {
      return true;
    }
    return node.tags.includes(tagforfilter);
  };

  useEffect(() => {
    axiosGraphInfo(
      "/graph_info").then(({ data }) => {
        setNodes(data.nodes);
        setEdges(data.edges);

        console.log(data.nodes);
        console.log(data.edges);
      });
  }, []);

  useEffect(() => {
    if (network) {
      network.destroy();
    }
    if (container.current) {

      const nodeData = new DataSet(nodes);

      const nodesView = new DataView(nodeData, {
        filter: nodeFilter,
      });
      
      const data = {
        nodes: nodes,
        edges: edges,
      };

      const options = {
        autoResize: true,
        height: "100%",
        width: "100%",
        clickToUse: false,
        nodes: {
          shape: "dot",
          size: 16,
        },
        interaction: {
          hover: true
        },
        physics: {
          forceAtlas2Based: {
            gravitationalConstant: -26,
            centralGravity: 0.005,
            springLength: 230,
            springConstant: 0.18,
          },
          maxVelocity: 146,
          solver: "forceAtlas2Based",
          timestep: 0.35,
          stabilization: { iterations: 150 },
        },
      };
      const _network = new Network(container.current, {
        nodes: nodesView,
        edges: edges,
      }, options);

      _network.on(
        "click",
        (params: any) => {
          console.log("MainGraph: click: params:", params);
          if (params.nodes.length > 0) {
            const nodeidx = params.nodes[0];
            const weburl = nodes[nodeidx].weburl;
            if (weburl) {
              window.open(weburl, "_blank");
            }
          }
        }
      )

      _network.on(
        'hoverNode',
        (params: any) => {
          //console.log("MainGraph: hoverNode: params:", params);
        }
      )

      setNetwork(
        _network
      );
    }
  }, [nodes, edges]);

  return (
    <div ref={container} style={{ position: "fixed", width: "100vw", height: "100vh" }} />
  );
};

export default MainGraph;