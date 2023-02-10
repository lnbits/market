function initNostrMarket(data) {
  console.log(data)
  let stalls = data.stalls.map(stall => {
    return {
      id: stall.id,
      name: stall.name,
      description: '',
      shipping: stall.shippingzones,
      products: data.products
        .filter(p => p.stall === stall.id)
        .map(p => ({
          id: p.id,
          name: p.product,
          description: p.description,
          categories: p.categories,
          amount: p.quantity,
          price: p.price,
          images: p.image && [
            p.image.startsWith('data:') ? p.image.slice(0, 20) : p.image
          ],
          action: null
        })),
      action: null
    }
  })
  return {
    name: '',
    description: '',
    currency: '',
    action: null,
    stalls
  }
}

function nostrStallData(data, action = 'update') {
  return {
    action,
    stalls: [
      {
        id: data.id,
        name: data.name,
        description: '',
        shipping: data.shippingzones,
        action
      }
    ]
  }
}

function nostrProductData(data, action = 'update') {
  let stallId = data.stall

  return {
    action,
    stalls: [
      {
        id: stallId,
        products: [
          {
            id: data.id,
            name: data.product,
            description: data.description,
            categories: data.categories,
            amount: data.quantity,
            price: data.price,
            images: data.image && [
              data.image.startsWith('data:')
                ? data.image.slice(0, 20)
                : data.image
            ],
            action: null
          }
        ]
      }
    ]
  }
}

async function subscribeToChatRelay(relay, pubkeys, cb = () => {}) {
  await relay.connect()

  relay.on('connect', () => {
    console.log(`connected to ${relay.url}`)
  })
  relay.on('error', () => {
    console.log(`failed to connect to ${relay.url}`)
  })

  let sub = relay.sub([
    {
      kinds: [4],
      authors: pubkeys
    },
    {
      kinds: [4],
      '#p': pubkeys
    }
  ])

  sub.on('event', event => {
    // console.log('we got the event we wanted:', event)
    cb(event)
  })

  sub.on('eose', () => {
    console.log('unsubscribed from', relay.url)
    sub.unsub()
  })
}

async function publishNostrEvent(relay, event) {
  //connect to relay
  await relay.connect()

  relay.on('connect', () => {
    console.log(`connected to ${relay.url}`)
  })
  relay.on('error', () => {
    console.log(`failed to connect to ${relay.url}`)
  })
  //publish event
  let pub = relay.publish(event)
  pub.on('ok', () => {
    console.log(`${relay.url} has accepted our event`)
  })
  pub.on('seen', () => {
    console.log(`we saw the event on ${relay.url}`)
    relay.close()
  })
  pub.on('failed', reason => {
    console.log(`failed to publish to ${relay.url}: ${reason}`)
    relay.close()
  })
  return
}

/*class RelayPool {
  constructor(relays, opts) {
    if (!(this instanceof RelayPool)) return new RelayPool(relays, opts)
    this.relays = []
    this.opts = opts

    for (const relay of relays) {
      this.add(relay)
    }

    return this
  }

  close() {
    for (const relay of this.relays) {
      relay.close()
    }
  }

  on(method, fn) {
    for (const relay of this.relays) {
      this.onfn[method] = fn
      relay.onfn[method] = fn.bind(null, relay)
    }
    return this
  }

  has(relayUrl) {
    for (const relay of this.relays) {
      if (relay.url === relayUrl) return true
    }

    return false
  }

  send(payload, relay_ids) {
    const relays = relay_ids ? this.find_relays(relay_ids) : this.relays
    for (const relay of relays) {
      relay.send(payload)
    }
  }

  setupHandlers() {
    // setup its message handlers with the ones we have already
    const keys = Object.keys(this.onfn)
    for (const handler of keys) {
      for (const relay of this.relays) {
        relay.onfn[handler] = this.onfn[handler].bind(null, relay)
      }
    }
  }

  remove(url) {
    let i = 0

    for (const relay of this.relays) {
      if (relay.url === url) {
        relay.ws && relay.ws.close()
        this.relays = this.replays.splice(i, 1)
        return true
      }

      i += 1
    }

    return false
  }

  subscribe(sub_id, filters, relay_ids) {
    const relays = relay_ids ? this.find_relays(relay_ids) : this.relays
    for (const relay of relays) {
      relay.subscribe(sub_id, filters)
    }
  }

  unsubscribe(sub_id, relay_ids) {
    const relays = relay_ids ? this.find_relays(relay_ids) : this.relays
    for (const relay of relays) {
      relay.unsubscribe(sub_id)
    }
  }

  add(relay) {
    if (relay instanceof Relay) {
      if (this.has(relay.url)) return false
      this.relays.push(relay)
      this.setupHandlers()
      return true
    }

    if (this.has(relay)) return false

    const r = new Relay(relay, this.opts)
    this.relays.push(r)
    this.setupHandlers()
    return true
  }

  find_relays(relay_ids) {
    if (relay_ids instanceof Relay) return [relay_ids];
  }
}

RelayPool.prototype.find_relays = function relayPoolFindRelays(relay_ids) {
  if (relay_ids instanceof Relay) return [relay_ids]

  if (relay_ids.length === 0) return []

  if (!relay_ids[0]) throw new Error('what!?')

  if (relay_ids[0] instanceof Relay) return relay_ids

  return this.relays.reduce((acc, relay) => {
    if (relay_ids.some(rid => relay.url === rid)) acc.push(relay)
    return acc
  }, [])
}*/
