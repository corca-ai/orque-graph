import { Network } from "vis-network";
import React, { useEffect, useState, useRef } from "react";
import axiosGraphInfo from "./axios";


const MainGraph = () => {
  const [nodes, setNodes] = useState<any>([]);
  const [edges, setEdges] = useState<any>([]);
  const [webs, setWebs] = useState<any>([]);
  const [network, setNetwork] = useState<Network>();
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axiosGraphInfo(
      "/graph_info").then(({ data }) => {
        setNodes(data.nodes);
        setEdges(data.edges);
        setWebs(data.webs);
      });

    //console.log("MainGraph: useEffect");
    //console.log("MainGraph: useEffect: nodes:", nodes);
  }, []);

  useEffect(() => {
    if (network) {
      network.destroy();
    }
    if (container.current) {
      var data = {
        nodes: nodes,
        edges: edges,
      };
      var options = {
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
      var _network = new Network(container.current, data, options);

      _network.on(
        "click",
        (params: any) => {
          console.log("MainGraph: click: params:", params);
          if (params.nodes.length > 0) {
            const nodeidx = params.nodes[0];
            const web = webs[nodeidx];
            //console.log("MainGraph: click: web:", web);
            // redirect to web
            window.location.href = web; 
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