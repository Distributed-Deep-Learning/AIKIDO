package kungfu

import (
	"sync"
	"time"

	"github.com/lsds/KungFu/srcs/go/log"
	"github.com/lsds/KungFu/srcs/go/plan"
	rch "github.com/lsds/KungFu/srcs/go/rchannel"
)

func (sess *session) GetPeerLatencies() []time.Duration {
	results := make([]time.Duration, len(sess.cluster.Peers))
	var wg sync.WaitGroup
	for rank, peer := range sess.cluster.Peers {
		if rank != sess.myRank {
			wg.Add(1)
			go func(rank int, peer plan.PeerSpec) {
				results[rank] = getLatency(*sess.self, peer)
				wg.Done()
			}(rank, peer)
		} else {
			results[rank] = 0
		}
	}
	wg.Wait()
	return results
}

func getLatency(self, peer plan.PeerSpec) time.Duration {
	t0 := time.Now()
	var conn rch.Connection
	for i := 0; i < 10; i++ {
		var err error
		conn, err = rch.NewPingConnection(self.NetAddr, peer.NetAddr)
		if err == nil {
			break
		}
		log.Warnf("connection %d failed for %v", i+1, err)
		time.Sleep(1 * time.Second)
	}
	if conn == nil {
		// connection failed
		return time.Since(t0)
	}
	defer conn.Close()
	t0 = time.Now() // reset t0
	var empty rch.Message
	conn.Send("ping", empty)
	conn.Read("ping", empty)
	// FIXME: handle timeout
	return time.Since(t0)
}